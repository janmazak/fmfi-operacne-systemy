#!/usr/bin/python3

import subprocess
import resource
import datetime
import threading
import tempfile
from html import escape
import sys
import os

SUBMITS = os.getcwd() + "/submits/"
COMMON = os.getcwd() + "/common/"

def colored(s,color):
	if color == "red":
		c="\033[0;31m"
	elif color == "green":
		c="\033[0;32m"

	return(c + s + "\033[00m")

def hex2list(h):
	return list(map(lambda x: int(x[0]+x[1], 16), list(zip(h[::2],h[1::2]))))

def lsb2msb(i):
	return i[6:8] + i[4:6] + i[2:4] + i[0:2]

class SubmitRun:
	def __init__(self, args):
		self.__args = args
		self.msize = int(args[-1])
		self.__cwd = tempfile.mkdtemp()
		self.reads = 0
		self.writes = 0

		self.start()

	def start(self):
		self.__p = subprocess.Popen(self.__args, cwd = self.__cwd, bufsize=1, stdin=subprocess.PIPE,
			stdout=subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, preexec_fn  =
			self.set_limits, close_fds=True)

	def __del__(self):
		try:
			#self.end()
			pass
		except IOError:
			pass
		os.system("rm -rf " + self.__cwd)

	def log(self, s):
		#print(s)
		pass

	def restart(self):
		self.end()
		self.start()

	def set_limits(self):
		#resource.setrlimit(resource.RLIMIT_CPU, (120,120))
		resource.setrlimit(resource.RLIMIT_CPU, (40,40))
		#resource.setrlimit(resource.RLIMIT_CPU, (120,120))
		#resource.setrlimit(resource.RLIMIT_CPU, (16,16))
		pass

	def send(self, s):
		try:
			self.__p.stdin.write(s)
		except BrokenPipeError:
			raise RuntimeError("Target terminated unexpectedly")

	def recv(self):
		s = self.__p.stdout.readline()
		return s

	def cmd(self, cmd, checkOkFailReturnValue=False, *args):
		pout = cmd + " " + " ".join(map(str, args))
		#print(pout)
		self.send(pout + "\n")

		pin = self.recv()
		self.log("%s: '%s'" % (pout,pin.strip()))
		if (pin==''):
			# Probably termination; try to wait
			self.__p.wait()
			if self.__p.returncode != None:
				code = self.__p.returncode
				if code == -9: raise RuntimeError("Timeout (command: %s)"%cmd)
				elif code > 0 or code == -6:
					err = self.__p.stderr.readlines()
					if err != []:
						raise RuntimeError(("Runtime error (command: %s):\n" % cmd) + "".join(err))
					else:
						raise RuntimeError("Runtime error (command: %s)" % cmd)
				elif code == -11:
					raise RuntimeError("Runtime error: segfault (command: %s)" % cmd)
				else: raise RuntimeError("Terminated with exit code %d (command: %s) " % (self.__p.returncode, cmd))
			else:
				raise RuntimeError("Unknown (command: %s)" % cmd)
		# Split results and r/w stats
		#print(pin, end='')

		(pin, stats) = pin.split("#")
		pin = pin.strip()
		items = pin.split(" ")

		# Decode reads/writes
		(reads, writes) = map(int, stats.strip().split(" "))
		self.reads += reads
		self.writes += writes
		if (len(items) == 1):
			ret = (int(items[0], 0), )
		else:
			ret = (
				int(items[0], 0),
				items[1]
			)

		value = ret[0]
		if checkOkFailReturnValue:
			OK = 0
			FAIL = -1
			if (value != OK) and (value != FAIL):
				raise RuntimeError("Invalid return value " + str(value))
		else:
			# should be an address
			if value < 0:
				raise RuntimeError("Invalid handle pointer value " + str(value))

		return ret

	def end(self):
		try:
			self.cmd("end", False)
		except (IOError, RuntimeError):
			pass
		self.__p.wait()

	# L1
	def open(self, path): return self.cmd("open", False, path)[0]
	def creat(self, path): return self.cmd("creat", False, path)[0]
	def close(self, fd): return self.cmd("close", True, fd)[0]
	def unlink(self, path): return self.cmd("unlink", True, path)[0]
	def rename(self, oldpath, newpath): return self.cmd("rename", True, oldpath, newpath)[0]

	def read(self, fd, length):
		ret = self.cmd("read", False, fd, length)
		if (len(ret) == 1):
			ret = (ret[0], '')

		# Black magic to decode hex byte string to list of bytes
		return (ret[0], list(map(lambda x: int(x[0]+x[1], 16),
			list(zip(ret[1][::2],ret[1][1::2])))))

	def write(self, fd, data):
		return self.cmd("write", False, fd, "".join(map(lambda x: hex(x)[2:],data)), len(data))[0]
	def seek(self, fd, pos): return self.cmd("seek", True, fd, pos)[0]
	def tell(self, fd): return self.cmd("tell", False, fd)[0]
	def stat(self, fd):
		ret = self.cmd("stat", True, fd)
		if len(ret) == 1:
			return ret[0]
		assert len(ret[1]) == 24
		rd = {
			'st_size': int(lsb2msb(ret[1][0:8]), 16),
			'st_nlink': int(lsb2msb(ret[1][8:16]), 16),
			'st_type': int(lsb2msb(ret[1][16:24]) ,16),
			}
		return (ret[0],rd)

	def mkdir(self, path): return self.cmd("mkdir", True, path)[0]
	def rmdir(self, path): return self.cmd("rmdir", True, path)[0]
	def opendir(self, path): return self.cmd("opendir", False, path)[0]
	def readdir(self, fd): return self.cmd("readdir", True, fd)
	def closedir(self, fd): return self.cmd("closedir", False, fd)[0]

	def link(self, oldpath, newpath): return self.cmd("link", True, oldpath, newpath)[0]
	def symlink(self, path, sympath): return self.cmd("symlink", True, path, sympath)[0]

def compile(source):
	csource = source + "/filesystem.c"
	jsource = source + "/Filesystem.java"
	if os.access(csource, os.R_OK):
		if source.find("sadovsky") != -1:
			append = "-std=gnu99"
		else: append=""
		os.system("cc -std=gnu99 -O0 -g %s -Icommon/c/ common/c/wrapper.c common/c/util.c -o %s -lm %s" % (csource,
			source + "/filesystem", append))
	elif os.access(jsource, os.R_OK):
		os.system("javac -cp "+source+":common/java %s" % (jsource))
	else:
		print("Unknown source for " + source)

def run(source, args):
	cbinary = source + "/filesystem"
	jbinary = source + "/Filesystem.class"
	if os.access(cbinary, os.R_OK):
		# Got binary
		run_args = [cbinary, "disk.img" ]
	elif os.access(jbinary, os.R_OK):
		run_args = ['java', '-ea', '-cp', source+':' + COMMON + '/java', 'Wrapper']
	else:
		print("Could not launch " + source)

	return SubmitRun(run_args + args)


class TestJob:
	def __init__(self, submit, testfn, **params):
		self.params = params
		self.submit = submit
		self.testfn = testfn
		self.__result = None

	def run(self):
		# Extract task-dependent params
		submit_run = run(SUBMITS + self.submit, [str(self.params['msize'])])
		assert submit_run is not None

		msg = ""
		ret = -1
		try:
			ret = self.testfn(submit_run, self.params['msize'])
		except RuntimeError as e:
			msg = "FAIL: %s" % str(e)
		except ValueError as e:
			msg = "Protocol error: %s" % str(e)
			self.__result = (ret, msg)
			return

		submit_run.end()


		if ret >= 0:
			msg = "OK: " + str(ret)
		self.__result = (ret, msg)

	def is_ok(self):
		if self.__result is None: return None

		if self.__result[0] >= 0:
			return True
		return False

	def message(self):
		if self.__result is None: return None

		return self.__result[1]

	def get_result(self):
		return self.__result

	def __str__(self):
		return "%s\t%8d\t%-40s" % (self.submit, self.params['msize'],
				self.testfn.__name__)


class TestRunner:
	def __init__(self, test_list, num_threads):
		self.test_list = test_list
		self.num_threads = num_threads
		self.queue = test_list[:]
		self.queue_lock = threading.Lock()
		self.console_lock = threading.Lock()

	def job_start(self, test):
		with self.console_lock:
			print("%s: START" % str(test))

	def job_finish(self, test):
		if test.is_ok(): color = 'green'
		else: color = 'red'

		msg = colored(test.message(), color)

		with self.console_lock:
			print("%s: %s" % (str(test), msg))

	def queue_runner(self):
		while True:
			with self.queue_lock:
				if len(self.queue) == 0:
					break
				test = self.queue.pop(0)

			self.job_start(test)
			test.run()

			self.job_finish(test)

	def run(self):
		threads = []
		for i in range(0, self.num_threads):
			thread = threading.Thread(target = self.queue_runner)
			thread.start()
			threads.append(thread)

		for thread in threads:
			thread.join()


# Load tests

tests_module = __import__("tests")
tests = list(map(lambda x: getattr(tests_module, x), filter(lambda x: x.startswith("test_"),
	dir(tests_module))))


memsizes = [32768]
#memsizes = [32768, 2**17, 2**19, 2**21 ]
mem_results = {}

if len(sys.argv) > 1:
	all_submits = sys.argv[1:]
else:
	all_submits = os.listdir(SUBMITS)

sys.stdout.write("Compiling... ")
for source in all_submits:
	sys.stdout.write(source + ", ")
	sys.stdout.flush()
	compile(SUBMITS + source)
print("ALL DONE")

jobs = []
for submit in all_submits:
	for msize in memsizes:
		for test in tests:
			jobs.append(TestJob(submit, test, msize = msize))

TestRunner(jobs, 1).run()

all_results = {}
for job in jobs:
	msize = job.params['msize']
	submit = job.submit

	mem_results.setdefault(msize, {})
	mem_results[msize].setdefault(submit,[None] * len(tests))

	mem_results[msize][submit][tests.index(job.testfn)] = job.get_result()

#for source in all_submits:
#	for msize in memsizes:
#		print("Memory size %d" % msize)
#		mem_results.setdefault(msize, {})
#		mem_results[msize].setdefault(source, [])
#		for test in tests:
#			clean(SUBMITS + source)
#			s = run(SUBMITS + source, [str(msize)])
#			sys.stdout.write("  %-40s" % str(test.__name__))
#			sys.stdout.flush()
#			res = -1
#			message = "OK"
#			try:
#				res = test(s, msize)
#			except RuntimeError as e:
#				message = "FAIL: %s" % str(e)
#
#			if res >= 0:
#				message = "OK: %d" % res
#				color = 'green'
#			else:
#				color = 'red'
#
#			mem_results[msize][source].append((res, message))
#			print(colored(message,color))

# Format HTML output

html = open("results.html", "w+")

html.write("<html>")
html.write("""
<head>
	<style type="text/css">
		.out { overflow: hidden; height: 1em; }
		.out:hover { overflow: none; height: auto; border: 1px solid;
		background-color: white; position: absolute; font-family: monospace; }
		td {overflow: visible; vertical-align: top; width: 20em; }
		table {table-layout: fixed; }
    </style>
</head>
""")
html.write("<body>")

for msize in mem_results.keys():
	results = mem_results[msize]
	submits = list(results.keys())
	submits.sort()

	html.write("<h2>%d bytes</h2>" % msize)
	html.write("<table border=\"2\">\n")

	# Calculate maximums across tests
	test_min = [0]*len(tests)
	for test in range(0,len(tests)):
		test_min[test] = 9999999999999
		for submit in submits:
			if results[submit][test] is None:
				print("Job did not run: %s, %s" % (submit, test))
				continue
			if results[submit][test][0] < 0:
				continue
			test_min[test] = min (test_min[test], results[submit][test][0])

	# Test header
	html.write("<thead><tr><td>User</td>")
	for test in tests:
		html.write("<td>%s</td>"% test.__name__[5:])
	html.write("</tr></thead>\n")

	for submit in submits:
		html.write("<tr><td>%s</td>" % submit);
		for test in range(0,len(results[submit])):
			item = results[submit][test]
			if item is None:
				html.write("<td>Test did not run</td>")
				continue
			if item[0] == -1:
				sty = "background-color: red"
			else:
				if test_min[test] == item[0]:
					sty = "background-color: lightgreen"
				else:
					sty = "background-color: green"
			html.write("<td style=\"%s\"><div class=\"out\">%s</div></td>" %
					(sty, escape(item[1]).replace("\n","<br/>\n")))
		html.write("</tr>\n")
	html.write("</table>")

html.write("Generated: %s</body></html>\n" % datetime.datetime.now().ctime())
html.close()

