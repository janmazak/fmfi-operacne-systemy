from math import sqrt, floor
from random import Random

OK = 0
FAIL = -1
NULL = 0

STAT_TYPE_FILE = 0
STAT_TYPE_DIR = 1
STAT_TYPE_SYMLINK = 2

# Utility functions
def if_raise(cond, s):
	if cond:
		raise RuntimeError(s)

def next_inode():
	next_inode.i+=1
	return next_inode.i
next_inode.i = 0
	
def parent(s):
	ret = s[:s.rfind('/')]
	if ret == '':
		ret = '/'

	return ret

def basename(s):
	ret = s[s.rfind('/')+1:]
	return ret

def tobuf(s):
	return list(map(ord,s))

# Tester class

class FilesystemTester:
	def __init__(self, s, dsize):
		self.s = s
		self.dsize = dsize
		self.fs = {'/': {'type':STAT_TYPE_DIR }}
		self.fd = {}
		self.pos = {}
		self.dirfd = {}
		self.inodes = {}
		self.inode_links = {}
		pass

	def ops(self):
		return self.s.reads + self.s.writes

	def children(self,path):
		if path == '/':
			prefix = '/'
		else:
			prefix = path + '/'
		all_children = filter(lambda x: x.startswith(prefix) and x != '/',
				self.fs.keys())
		direct_children = filter(lambda x: x[len(path)+1:].find('/') == -1,	all_children)
		return list(direct_children)

	def my_unlink(self, path):
		''' Performs unlink only in local file structures '''
		if (self.fs[path]['type'] != STAT_TYPE_DIR):
			inode = self.fs[path]['inode']
			if (self.fs[path]['type'] == STAT_TYPE_FILE):
				self.inode_links[inode] -= 1
				if self.inode_links[inode] == 0:
					del self.inode_links[inode]
					del self.inodes[inode]
			del self.fs[path]

	def creat(self, path):
		fd = self.s.creat(path)

		if fd == NULL:
			if_raise(path in self.fs.keys(), "Could not truncate file")
			if_raise(path not in self.fs.keys(), "Could not create file")
		else:
			if_raise(path in self.fs.keys() and (self.fs[path]['type'] == STAT_TYPE_DIRECTORY),
				"Creat would overwrite a directory")

		# remove path if it exists and is not directory
		if path in self.fs.keys():
			self.my_unlink(path)

		inode = next_inode()
		self.fs[path] = {"inode": inode, "type": STAT_TYPE_FILE }
		self.inodes[inode] = []
		self.inode_links[inode] = 1
		self.fd[fd] = path
		self.pos[fd] = 0

		return fd

	def open(self, path):
		fd = self.s.open(path)

		assert path not in self.fd.values()

		if fd == NULL:
			if_raise(path in self.fs.keys(), "Existing file not opened")
		else:
			if_raise(path not in self.fs.keys(), "Non-existent file opened")

		if (path in self.fs.keys()) and (self.fs[path]['type'] == STAT_TYPE_SYMLINK):
			path = self.fs[path]['dest']
			if fd == NULL:
				if_raise(path in self.fs.keys(), "Existing symlink target not opened")
			else:
				if_raise(path not in self.fs.keys(), "Non-existent symlink target opened")

		if path in self.fs.keys():
			self.fd[fd] = path
			self.pos[fd] = 0

		return fd

	def close(self, fd):
		ret = self.s.close(fd)

		if_raise(ret != OK, "Close failed when it should not")

		del self.fd[fd]
		del self.pos[fd]

		return ret

	def read(self, fd, size):
		assert fd in self.fd.keys()

		ret = self.s.read(fd, size)
		if_raise(ret[0] > size, "Read more data than requested")

		curpos = self.pos[fd]
		fname = self.fd[fd]
		inode = self.fs[fname]['inode']
		data = self.inodes[inode][curpos:curpos + size]

		if_raise(len(data) > ret[0], "Short read where data available")
		if_raise(len(data) < ret[0], "Read more than exists in file")
		if_raise(data != ret[1], "Data mismatch while reading")

		self.pos[fd] += ret[0]

		return ret
		
	def write(self, fd, data):
		assert fd in self.fd.keys()

		ret = self.s.write(fd, data)
		written = ret

		if_raise(written > len(data), "Wow! Wrote more data than supplied (len %d, write %d)" % (len(data), written) )
		if_raise(written < len(data), "Short write (len %d, wrote %d)" % (len(data), written))

		curpos = self.pos[fd]
		fname = self.fd[fd]
		inode = self.fs[fname]['inode']
		
		content = self.inodes[inode]
		self.inodes[inode] = content[0:curpos] + data[0:written] + content[curpos+written:]
		self.pos[fd] += written

		return ret

	def unlink(self, path):
		ret = self.s.unlink(path)
		assert path not in self.fd.values()

		if ret == FAIL:
			if_raise((path in self.fs.keys() and (self.fs[path]['type'] != STAT_TYPE_DIR)),
				"Unlink on existing file failed")
		else:
			if_raise(path not in self.fs.keys(), "Unlink on non-existent file succeeded")
			if_raise((path in self.fs.keys() and self.fs[path]['type'] == STAT_TYPE_DIR),
				"Unlink of directory succeeded")

		if path not in self.fs.keys():
			return ret

		self.my_unlink(path)
		return ret

	def rename(self, oldpath, newpath):
		ret = self.s.rename(oldpath,newpath)
		assert oldpath not in self.fd.values()
		assert newpath not in self.fd.values()
		
		if_raise((oldpath not in self.fs.keys() and (ret != FAIL)),
			"Rename on non-existent file succeeded")
		assert oldpath in self.fs.keys()
		
		if_raise((newpath in self.fs.keys() and (self.fs[newpath]['type'] ==
			STAT_TYPE_DIR) and (self.fs[oldpath]['type'] != STAT_TYPE_DIR) and (ret != FAIL)),
			"Renaming directory to existing file")
		if_raise((newpath in self.fs.keys() and (self.fs[newpath]['type'] !=
			STAT_TYPE_DIR) and (self.fs[oldpath]['type'] == STAT_TYPE_DIR) and (ret != FAIL)),
			"Renaming existing file to directory")
		if_raise((newpath in self.fs.keys() and (self.fs[newpath]['type'] !=
			STAT_TYPE_DIR) and (newpath not in self.fs.keys()) and (ret == FAIL)),
			"Could not rename existing file")
		
		# Rename all matching items
		keys = list(self.fs.keys())
		for key in keys:
			if not key.startswith(oldpath):
				continue

			suffix = key[len(oldpath):]
			self.fs[newpath + suffix] = self.fs[oldpath]
			del self.fs[oldpath]

		return ret

	def tell(self, fd):
		ret = self.s.tell(fd)
		if_raise(ret != self.pos[fd], "Invalid file position from tell (expected %d, got %d)" % (self.pos[fd], ret))
		return ret
	
	def seek(self, fd, pos):
		ret = self.s.seek(fd, pos)

		fname = self.fd[fd]
		inode = self.fs[fname]['inode']
		flen = len(self.inodes[inode])

		if_raise((pos > flen) and ret == OK,
			"Seek outside file succeeded (pos %d, len %d)" % (pos, flen) )

		if_raise((pos <= flen) and ret == FAIL,
			"Seek to %d inside file of size %d failed"% (pos, flen ))
		
		if ret == OK:
			self.pos[fd] = pos

		return ret

	def stat(self, path):
		ret = self.s.stat(path)

		if_raise((path not in self.fs.keys()) and (ret != FAIL),
				"Stat for non-existent file succeeded")

		if ret == FAIL:
			return ret
		
		if self.fs[path]['type'] == STAT_TYPE_FILE:
			inode = self.fs[path]['inode']

			if_raise(len(self.inodes[inode]) != ret[1]['st_size'],
					"Recorded size different than real")
			if_raise(ret[1]['st_nlink'] != self.inode_links[inode],
					"Incorrect number of links")
			if_raise(self.fs[path]['type'] != ret[1]['st_type'],
					"Incorrect item type")
		elif self.fs[path]['type'] == STAT_TYPE_DIR:
			if_raise(ret[1]['st_nlink'] != 1,
					"Directory has more than one link to itself")

		return ret

	def mkdir(self, path):
		ret = self.s.mkdir(path)
	
		path_existed = path in self.fs.keys()

		if path not in self.fs.keys():
			self.fs[path] = { 'type': STAT_TYPE_DIR }
			myret = OK
		else:
			myret = FAIL
			
		if_raise(path_existed and (ret != FAIL),
			"Mkdir on existent directory succeeded")
		if_raise((not path_existed) and (ret == FAIL),
			"Mkdir failed")

		assert myret == ret	# Some case is not handled

		return ret
	
	def rmdir(self, path):
		ret = self.s.rmdir(path)

		path_existed = path in self.fs.keys()
		if_raise(path_existed and (self.fs[path]['type'] != STAT_TYPE_DIR) and (ret != FAIL),
			"Rmdir succeeded on non-directory")
		if_raise((path_existed and (len(self.children(path)) == 0) and (ret == FAIL)),
			"Rmdir on existent empty directory failed")
		if_raise((path_existed and (len(self.children(path)) != 0) and (ret != FAIL)),
			"Rmdir succeeded on non-empty directory")
		if_raise(((not path_existed)  and (ret != FAIL)),
			"Rmdir on non-existent directory succeeded")

		if (path not in self.fs.keys()):
			myret = FAIL
		elif (self.fs[path]['type'] != STAT_TYPE_DIR):
			myret = FAIL
		elif (len(self.children(path)) != 0):
			myret = FAIL
		else:
			del self.fs[path]
			myret = OK

		assert myret == ret

		return ret

	def opendir(self, path):
		ret = self.s.opendir(path)
		
		if path in self.fs.keys() and self.fs[path]['type'] == STAT_TYPE_SYMLINK:
			path = self.fs[path]['dest']

		if_raise((path not in self.fs.keys() and (ret != NULL)),
			"Opendir on non-existent directory succeeded")
		if_raise((path in self.fs.keys() and (ret == NULL)),
			"Opendir on existing directory failed")
		if_raise((path in self.fs.keys() and (self.fs[path]['type'] != STAT_TYPE_DIR) and (ret != NULL)),
			"Opendir on non-directory succeeded")

		assert ret >= 0
		#if path in self.fs.keys() and self.
		self.dirfd[ret] = (path, set())

		return ret

	def closedir(self, dirfd):
		assert dirfd in self.dirfd

		ret = self.s.closedir(dirfd)

		if_raise(ret == FAIL, "Closedir failed")

		del self.dirfd[dirfd]

		return ret

	def readdir(self, dirfd):
		ret = self.s.readdir(dirfd)
		path = self.dirfd[dirfd][0]
		
		children_names = map(basename, self.children(path))
		read_children_names = self.dirfd[dirfd][1]

		if len(ret) > 1:
			if_raise((ret[1] not in children_names) and (ret[0] != FAIL),
					"Readdir listed unknown child: " + ret[1] + " in "+
					str(list(children_names)))
		if_raise((ret[0] == FAIL) and (set(children_names) != read_children_names),
			"Child list not complete")

		if ret[0] != FAIL:
			read_children_names.add(ret[1])

		return ret
		
	def link(self, oldpath, newpath):
		ret = self.s.link(oldpath, newpath)
		if_raise((oldpath not in self.fs.keys()) and (ret != FAIL),
			"Link from non-existent file succeeded")
		if_raise((oldpath in self.fs.keys()) and (self.fs[oldpath]['type'] ==
			STAT_TYPE_DIR) and (ret != FAIL),
			"Linking directory succeeded")

		if_raise((newpath in self.fs.keys()) and (self.fs[newpath]['type'] ==
			STAT_TYPE_DIR) and (ret != FAIL),
			"Directory as link destination succeeded")

		if_raise(
				(oldpath in self.fs.keys()) and (self.fs[oldpath]['type'] !=STAT_TYPE_DIR) and
				(newpath not in self.fs.keys() or (
				 newpath in self.keys() and (self.fs[newpath]['type']  !=STAT_TYPE_DIR)))
				and (ret == FAIL),
			"Link creation failed")

		if newpath in self.fs.keys():
			if self.fs[newpath]['type'] == STAT_TYPE_DIRECTORY:
				return ret
			self.my_unlink(newpath)	

		if oldpath not in self.fs.keys():
			return ret

		if oldpath in self.fs.keys() and self.fs[oldpath]['type'] == STAT_TYPE_DIR:
			return ret

		# newpath does not exist, oldpath is correct
		inode = self.fs[oldpath]['inode']
		self.fs[newpath] = {'type': STAT_TYPE_FILE, 'inode': inode }
		self.inode_links[inode] += 1

		return ret

	def symlink(self, oldpath, newpath):
		ret = self.s.symlink(oldpath, newpath)

		if_raise((newpath in self.fs.keys()) and (self.fs[newpath]['type'] ==
			STAT_TYPE_DIR) and (ret != FAIL),
			"Directory as symlink destination succeeded")

		if_raise(ret == FAIL,
			"Symlink creation failed")

		if newpath in self.fs.keys():
			if self.fs[newpath]['type'] == STAT_TYPE_DIRECTORY:
				# we can't rewrite directories
				return ret
			self.my_unlink(newpath)


		# newpath does not exist, oldpath is correct
		self.fs[newpath] = {'type': STAT_TYPE_SYMLINK, 'dest': oldpath }

		return ret

def test_01_creat_open_close(s, dsize):
	t = FilesystemTester(s, dsize)

	# This should fail
	ret = t.open("/test.txt")
	assert ret == NULL

	ret = t.creat("/test.txt")
	t.close(ret)

	ret = t.open("/test.txt")
	t.close(ret)

	return t.ops()

def test_01_unlink(s, dsize):
	t = FilesystemTester(s, dsize)
	
	assert t.open("/test.txt") == NULL
	
	ret = t.creat("/test.txt")
	t.close(ret)

	ret = t.open("/test.txt")
	t.close(ret)

	t.unlink("/test.txt")
	ret = t.open("/test.txt")

	return t.ops()
	
def test_01_rename(s, dsize):
	t = FilesystemTester(s, dsize)
	oldfile="/test.txt"
	newfile="/testnew.txt"
	
	t.close(t.creat(oldfile))
	ret = t.rename(oldfile, newfile)
	if_raise(ret == FAIL, "Rename failed")

	t.open(oldfile)	# Should fail
	t.close(t.open(newfile))
	
	t.unlink(oldfile)
	t.unlink(newfile)
	return t.ops()
	

def test_02_hello_world(s, dsize):
	t = FilesystemTester(s, dsize)
	
	test_string = tobuf("Hello, world")
	test_file = "/test.txt"
	
	fd = t.creat(test_file)
	t.close(fd)

	fd = t.open(test_file)
	ret = t.read(fd, len(test_string))
	t.close(fd)

	return t.ops()

def test_02_hello_world_seek(s, dsize):
	t = FilesystemTester(s, dsize)
	test_string = tobuf("Hello, world")
	test_file = "/test.txt"
	
	fd = t.creat(test_file)
	t.write(fd, test_string)
	
	t.tell(fd)
	t.seek(fd,0)
	t.tell(fd)

	t.write(fd, list(map(ord,"Ahoj")))
	t.seek(fd, 11)
	t.write(fd, [ord("!")])
	
	ret = t.read(fd, len(test_string))

	return t.ops()

def test_02_hello_world_rename(s, dsize):
	t = FilesystemTester(s, dsize)
	
	test_string = tobuf("Hello, world")
	test_file = "/test.txt"
	rename_file = "/rename.txt"
	
	fd = t.creat(test_file)
	t.close(fd)

	t.rename(test_file, rename_file)

	fd = t.open(rename_file)
	ret = t.read(fd, len(test_string))

	return t.ops()

def test_02_hello_world_stat(s, dsize):
	''' Simple stat test '''
	t = FilesystemTester(s, dsize)
	test_string = tobuf("Hello, world")
	test_file = "/test.txt"

	stat = t.stat(test_file)
	fd = t.creat(test_file)

	stat = t.stat(test_file)

	return t.ops()

def test_02_stress_creat(s, dsize):
	''' Create empty files using ratio 1 file er 4 sectors of disk size '''
	t = FilesystemTester(s, dsize)

	# Four sectors for file without any content
	count = min(int(dsize/(128*4)), 32767)
	for i in range(1, count):		
		test_file = "/t%04x.txt" % (i,)
		f = t.creat(test_file)
		t.close(f)
	return t.ops()

def test_02_stress_creat_write_read(s, dsize):
	''' Generates lots of small files, with reserve 6 sectors/file '''
	t = FilesystemTester(s, dsize)

	# Six sectors for file with content fitting into one block
	count = max(1,min(int(dsize/(128*6)), 32767))
	for i in range(1, count):
		test_file = "/t%04x.txt" % (i,)
		f = t.creat(test_file)
		assert f != FAIL
		t.write(f, tobuf("Hello, %04x" %(i)))
		t.close(f)
	
	for i in range(1, count):
		test_file = "/t%04x.txt" % (i,)
		f = t.open(test_file)
		assert f != FAIL
		t.read(f, 47)
		t.close(f)
		t.unlink(test_file)
	return t.ops()

def test_02_hello_bloat(s, dsize):
	''' Generates large files, which should in size fill up to 1/3 of disk space
	'''
	t = FilesystemTester(s, dsize)
	buff = tobuf("Hello, bloat")
	times = 512

	count = min(int(floor(dsize/(len(buff)*times*3))), 32767)
	for i in range(1, count):
		test_file = "/t%04x.txt" % (i,)
		f = t.creat(test_file)
		for i in range(1,times):
			t.write(f,buff)
		t.close(f)
	
	for i in range(1, count):
		test_file = "/t%04x.txt" % (i,)
		f = t.open(test_file)
		for i in range(1,times+1):
			t.read(f, len(buff))
		t.close(f)
		t.unlink(test_file)
	return t.ops()

#
#	Level 3 
#


def test_03_mkdir_rmdir(s, dsize):
	t = FilesystemTester(s, dsize)
	testdir = '/test'
	testfile = '/test/file'
	testdata = 'Hello, kitty'
	
	t.mkdir(testdir)

	f = t.creat(testfile)
	t.write(f, tobuf(testdata))
	t.seek(f, 0)
	t.read(f, len(testdata)+1)
	t.close(f)

	t.unlink(testdir) # Should fail
	t.rmdir(testdir) # Should fail, as there is file in directory

	t.unlink(testfile)
	t.unlink(testdir) # Should also fail
	t.rmdir(testdir)

	return t.ops()

def test_03_readdir(s, dsize):
	t = FilesystemTester(s, dsize)

	d = t.opendir('/')
	while t.readdir(d)[0] != FAIL:
		pass
	t.closedir(d)

	t.mkdir('/test')
	t.close(t.creat('/test/file1'))
	t.close(t.creat('/test/file2'))
	t.close(t.creat('/test/file3'))
	t.close(t.creat('/test/file4'))
	t.mkdir('/test/test2')

	d = t.opendir('/')
	while t.readdir(d)[0] != FAIL:
		pass
	t.closedir(d)

	d = t.opendir('/test')
	while t.readdir(d)[0] != FAIL:
		pass
	t.closedir(d)
	return t.ops()

def test_03_walktree(s, dsize):
	t = FilesystemTester(s, dsize)
	items = ['kalerab', 'mrkva',  'hruska', 'banan', 'coeste' ]

	def create_tree(root):
		if root.count('/') > 3:
			return

		for i in items:
			if (len(i) % 2 == 0):
				t.mkdir(root + i)
				create_tree(root + i + '/')
			else:
				f = t.creat(root + i)
				t.write(f, tobuf(i*15))
				t.close(f)

	def walk_tree(root):
		if root == '/':
			d = t.opendir(root)
		else:
			d = t.opendir(root[:-1])

		while True:
			ret = t.readdir(d)
			if ret[0] == FAIL:
				break

			path = root + ret[1]
			stat = t.stat(path)
			if stat != -1:
				if stat[1]['st_type'] == STAT_TYPE_DIR:
					walk_tree(path + '/')
				elif stat[1]['st_type'] == STAT_TYPE_FILE:
					f = t.open(path)
					while t.read(f, 256)[0] != 0: pass
					t.close(f)
				else:
					raise RuntimeError("Unknown file type")
			else:
				raise RuntimeError("Invalid data from stat")


	create_tree('/')
	walk_tree('/')
	return t.ops()

def test_04_link(s, dsize):
	t = FilesystemTester(s, dsize)
	testfile = '/test.txt'
	testlink = '/link.txt'
	testdir = '/dir'
	testdata = tobuf('Hello, kitty')
	testdata2 = tobuf('Sayonara, whale')

	t.mkdir(testdir)
	f = t.creat(testfile)
	t.write(f, testdata)
	t.close(f)

	assert t.link(testdir, testdir+'2') == FAIL	# Should fail
	assert t.link(testfile, testfile+'2') != FAIL	# Should succeed

	f = t.open(testfile + '2')
	t.read(f, len(testdata) + 1)
	t.seek(f, 0)
	t.write(f,testdata2)
	t.close(f)

	f = t.open(testfile)
	t.read(f, len(testdata2) + 1)
	t.close(f)

	return t.ops()

def test_04_symlink(s, dsize):
	t = FilesystemTester(s, dsize)
	testfile = '/test.txt'
	testlink = '/link.txt'
	testdir = '/dir'
	testdata = tobuf('Hello, kitty')
	testdata2 = tobuf('Sayonara, whale')

	t.mkdir(testdir)
	f = t.creat(testfile)
	t.write(f, testdata)
	t.close(f)

	assert t.symlink(testdir, testdir+'2') != FAIL
	assert t.symlink(testfile, testfile+'2') != FAIL

	f = t.open(testfile + '2')
	t.read(f, len(testdata) + 1)
	t.seek(f, 0)
	t.write(f,testdata2)
	t.close(f)

	f = t.open(testfile)
	t.read(f, len(testdata2) + 1)
	t.close(f)

	f = t.opendir(testdir+'2')
	while t.readdir(f)[0] != FAIL: pass
	t.closedir(f)

	return t.ops()
