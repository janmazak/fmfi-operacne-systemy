from math import sqrt
from random import Random
OK = 0
FAIL = -1

def overlap(a,b):
    if a[0] > b[0]:
        (a,b) = (b,a)
    return a[0] <= b[0] < a[0] + a[1]


def small_fixed_size(memsize):
    return 10 + memsize // 150


def medium_fixed_size(memsize):
    return 10 + memsize // 27


def doprimes(n): 
    if n==2: return [2]
    elif n<2: return []
    s=list(range(3,n+2,2))
    mroot = n ** 0.5
    half=(n+1)/2-1
    i=0
    m=3
    while m <= mroot:
        if s[i]:
            j=(m*m-3)//2
            s[j]=0
            while j<half:
                s[j]=0
                j+=m
        i=i+1
        m=2*i+3
    return [2]+[x for x in s if x]


class AllocTester:
    def __init__(self, s, msize):
        self.allocations = {}
        self.allocd = []
        self.s = s
        self.msize = msize
        self.moccupied = 0
        self.max_moccupied = 0
    
    def alloc(self, size):
        ret = self.s.alloc(size)
        if ret >= 0:
            if size + ret - 1 > self.msize - 1:
                raise RuntimeError("Byte exceeding maximum address allocated (ptr %d, size %d)" % (ret, size))

            for i in self.allocations.items():
                if overlap(i, (ret, size)):
                    raise RuntimeError("Allocated area overlap: (ptr %d, size %d), (ptr %d, size %d)" % (i[0], i[1], ret, size) )

            # Do some math...
            self.allocations[ret] = size
            self.allocd.append(ret)
            self.moccupied += size
            self.max_moccupied = max (self.moccupied, self.max_moccupied)
        return ret

    def free(self, addr):
        ret = self.s.free(addr)
        
        # Valid attempt to free
        if addr in self.allocations and (ret == FAIL):
                raise RuntimeError("Valid area not freed (%d)" % addr)
        if (addr not in self.allocations):
            if ret == OK:
                raise RuntimeError("Invalid area freed (%d)" % addr)
            else:
                # Everything's OK; nothing allocated, nothing freed
                return ret
        self.moccupied -= self.allocations[addr]
        del self.allocations[addr]
        self.allocd.remove(addr)

        return ret

    def restart_target(self):
        self.s.restart()

    def memcpy(self, dest, data):
        for i in range(0,len(data)):
            assert self.s.write(dest+i, data[i]) == OK
        assert self.memcmp(dest, data) == True
    
    def memcmp(self, dest, data):
        for i in range(0, len(data)):
            ret = self.s.read(dest + i)
            assert ret != FAIL
            if ret != data[i]:
                return False
        return True

    def compare(self, dest, data):
        if not self.memcmp(dest, data):
            raise RuntimeError("Data mismatch")

def test_01_alloc_small(s, msize):
    ''' Allocates all available memory and attempts to free pointers in the same
    order as they were returned '''
    tester = AllocTester(s, msize)
    mem = 0
    
    # Allocate memory until possible
    while tester.alloc(small_fixed_size(msize)) != FAIL: pass
    
    tester.restart_target()

    # Free memory
    while not len(tester.allocd) == 0:
        tester.free(tester.allocd[0])

    assert tester.moccupied == 0
    return tester.max_moccupied


def test_01_alloc_small_free_reverse(s, msize):
    ''' Allocates all available memory and attempts to free pointers in reverse
    order '''
    tester = AllocTester(s, msize)
    mem = 0
    
    # Allocate memory until possible
    while tester.alloc(small_fixed_size(msize)) != FAIL: pass
        
    tester.restart_target()
    
    # Free memory
    while not len(tester.allocd) == 0:
        tester.free(tester.allocd[-1])

    assert tester.moccupied == 0
    return tester.max_moccupied

def test_01_alloc_free_alloc_free(s, msize):
    t1 = test_01_alloc_small(s, msize)
    t2 = test_01_alloc_small_free_reverse (s, msize)

    if t1 != t2:
        raise RuntimeError("Could not reclaim all space")

    return max(t1,t2)


def test_01_alloc_medium_free_rand(s, msize):
    ''' Allocates all available memory, attempts to free all addresses in
    non-linear order '''    
    tester = AllocTester(s, msize)
    mem = 0
    
    # Allocate memory until possible
    while tester.alloc(medium_fixed_size(msize)) != FAIL: pass
    
    tester.restart_target()
        
    # Free memory
    for i in range(0, msize):
        tester.free((47*i) % msize)

    assert tester.moccupied == 0
    return tester.max_moccupied

def test_02_alloc_max(s, msize):
    tester = AllocTester(s, msize)
    lo = 1 
    hi = msize + 47
    
    while lo < hi:
        size = (lo + hi)//2
        ret = tester.alloc(size)

        if ret != FAIL:
            tester.free(ret)
            lo = size + 1
        else:
            hi = size
        


        assert hi > 0
    
    ret = tester.alloc(tester.max_moccupied)
    if ret == FAIL:
        raise RuntimeError("Could not alloc-free-alloc maximum");
    tester.free(ret)

    maximum_plus_one = tester.alloc(tester.max_moccupied + 1)
    if maximum_plus_one != FAIL:
        raise RuntimeError("Could not allocate %d bytes, but could allocate %d bytes" % (tester.max_moccupied, tester.max_moccupied+1) )

    assert tester.moccupied == 0
    return tester.max_moccupied

def test_02_alloc_256s_fill_rand_free_rand(s, msize):
    tester = AllocTester(s, msize)

    while True:
        ret = tester.alloc(256)
        if ret == FAIL: break
        tester.memcpy(ret, range(0,256))
    
    # Free memory
    for i in range(0, msize):
        tester.free((47*i) % msize)

    assert tester.moccupied == 0
    return tester.max_moccupied

def test_02_alloc_medium_fill_free(s, msize):
    ''' Allocates all available memory, attempts to free all addresses in
    non-linear order '''    
    tester = AllocTester(s, msize)
    mem = 0
    size = medium_fixed_size(msize)

    # Allocate memory until possible
    while True:
        ret = tester.alloc(size)
        if ret == FAIL: break
        tester.memcpy(ret, [47]*size)
    
    tester.restart_target()
        
    # Free memory
    for i in range(0, msize):
        if i in tester.allocd:
            tester.compare(i, [47]*size)
        tester.free((47*i) % msize)

    assert tester.moccupied == 0
    return tester.max_moccupied

def test_03_alloc_prime_sizes(s, msize):
    tester = AllocTester(s, msize)

    # Primes
    primes = doprimes(min(5000, msize))
    
    count = 0
    signs = {}
    while True:
        size = primes[count]
        ret = tester.alloc(size)
        if ret == FAIL: break
        signs[ret] = [size % 256]
        tester.memcpy(ret + size - 1, signs[ret])

        count += 1
    
    # Test written values
    for addr in tester.allocd:
        size = tester.allocations[addr]
        tester.memcmp(addr + size - 1, signs[addr])

    # Free even allocations
    to_free = []
    for i in range(0, len(tester.allocd)):
        if i % 2 == 0: to_free.append(tester.allocd[i])

    for i in range(0,len(to_free)):
        tester.free(to_free[i])

    tester.restart_target()
    # Test again, so overwrites will show up
    for addr in tester.allocd:
        size = tester.allocations[addr]
        tester.memcmp(addr + size - 1, signs[addr])

    while True:
        if tester.alloc(1) == FAIL: break
    
    to_free = tester.allocd[:]
    to_free.sort()

    for i in to_free: tester.free(i)

    assert tester.moccupied == 0
    return tester.max_moccupied 


def test_03_alloc_free_mix(s, msize):
    tester = AllocTester(s, msize)
    r = Random()
    r.seed(47)

    for i in range(1,int(msize/4)):
        what = r.randint(0,2)

        if what < 2:
            # Allocate memory
            tester.alloc(r.randint(1, medium_fixed_size(msize)))
        else:
            if len(tester.allocd) > 0:
                tester.free(r.choice(tester.allocd))

    return tester.max_moccupied


def test_04_alloc_free_mix_large(s, msize):
    tester = AllocTester(s, msize)
    r = Random()
    r.seed(47)

    steps = 5000
    for i in range(0, steps):
        what = r.randint(0,2)

        if what < 2:
            # Allocate memory
            tester.alloc(r.randint(1,int(msize)))
        else:
            if len(tester.allocd) > 0:
                tester.free(r.choice(tester.allocd))

    return tester.max_moccupied


