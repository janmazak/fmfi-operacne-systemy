#!/usr/bin/python3

import subprocess
import resource
import datetime
import threading
import tempfile
import fcntl
from html import escape
import sys
import os

SUBMITS = os.getcwd() + "/submits/"
COMMON = os.getcwd() + "/common/" 

TIMEOUT = 1

def colored(s,color):
    if color == "red":
        c="\033[0;31m"
    elif color == "green":
        c="\033[0;32m"
        
    return(c + s + "\033[00m")

class SubmitRun:
    def __init__(self, args, logfile = None):
        self.__args = args
        self.msize = int(args[-1])
        self.__cwd = tempfile.mkdtemp()
        self.errors = []
        self.logfile = logfile

        self.start()

    def start(self):
        self.__p = subprocess.Popen(self.__args, cwd = self.__cwd, bufsize=1, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, preexec_fn  =
            self.set_limits, close_fds=True)

# Make standard error output pollable
        fd = self.__p.stderr.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    def __del__(self):
        try:
            self.end()
        except IOError:
            pass
        os.system("rm -rf " + self.__cwd)

    def log(self, s):
        if self.logfile is not None:
            self.logfile.write(s + "\n")
        #print(s)
        pass

    def restart(self):
        self.end()
        self.start()

    def set_limits(self):
        #resource.setrlimit(resource.RLIMIT_CPU, (180,180))
        resource.setrlimit(resource.RLIMIT_CPU, (40,40))
        pass

    def send(self, s):
        self.__p.stdin.write(s)
        self.__p.stdin.flush()

    def recv(self):
        #print("trying readline") 
        s = self.__p.stdout.readline()
        #print("done readline") 

# stderr is non-blocking; no data returned cause problems with encoding
# conversion. For now catch it.

        try:
            err = self.__p.stderr.read()
            if err is not None:
                self.errors.append(err)
        except TypeError:
            pass
        return s

    def cmd(self, cmd, wait_reply = True, *args):
        try:
            pout = cmd + " " + " ".join(map(str,args))
            self.send(pout + "\n")

            if not wait_reply:
                self.log("%s" % (pout))
                return None

            pin = self.recv()
            self.log("%s: '%s'" % (pout,pin.strip()))
            if (pin==''):
                # Probably termination; try to wait
                self.__p.wait(timeout=TIMEOUT)
                if self.__p.returncode != None:
                    code = self.__p.returncode
                    if code == -9: raise RuntimeError("Timeout")
                    elif code > 0 or code == -6: 
                        err = self.errors
                        if err != []:
                            raise RuntimeError("Runtime error:\n" + "".join(err))
                        else:
                            raise RuntimeError("Runtime error")
                    elif code == -11:
                        raise RuntimeError("Runtime error: segfault")
                    else: raise RuntimeError("Terminated with exit code %d" % self.__p.returncode)
                else:
                    raise RuntimeError("Unknown")
            
            ret = int(pin)
            return ret
        except ValueError as e:
            raise RuntimeError("Protocol error: " + str(e))
    
    def end(self):
        try:
            self.cmd("end", False)
        except IOError:
            pass
        self.__p.wait(timeout=TIMEOUT)

    def alloc(self, size):
        ret = self.cmd("alloc", True, size)
        if ret < -1:
            raise RuntimeError("alloc: Unknown return value %d" % ret)
        return ret

    def free(self, addr):
        ret = self.cmd("free", True, addr)
        if ret not in [-1, 0]:
            raise RuntimeError("free: Unknown return value %d" % ret)
        return ret

    def read(self, addr):
        assert 0 <= addr < self.msize
        return self.cmd("read", True, addr)

    def write(self, addr, val):
        assert 0 <= addr < self.msize
        assert 0 <= val < 256
        return self.cmd("write", True, addr, val)


def compile(source):
    csource = source + "/alloc.c"
    jsource = source + "/Alloc.java"
    if os.access(csource, os.R_OK):
        if source.find("sadovsky") != -1:
            append = "-std=gnu99"
        else: append=""
        exit_code = os.system("cc -std=c99 -g %s -Icommon/c/ common/c/wrapper.c -o %s -lm %s" % (csource,
            source + "/alloc", append))
    elif os.access(jsource, os.R_OK):
        exit_code = os.system("javac -cp common/java/ %s" % (source +
            "/Alloc.java"))
    else:
        print("Unknown source for " + source)

    assert exit_code == 0

def run(source, args, logfile = None):
    cbinary = source + "/alloc"
#    jbinary = source + "/Alloc.class"
    if os.access(cbinary, os.R_OK):
        # Got binary
        run_args = [cbinary]
#    elif os.access(jbinary, os.R_OK):
#        run_args = ['java', '-ea', '-cp', source+':' + COMMON + '/java', 'Wrapper']
    else:
        print("Could not launch " + source)

    return SubmitRun(run_args + args, logfile = logfile)


class TestJob:
    def __init__(self, submit, testfn, **params):
        self.params = params
        self.submit = submit
        self.testfn = testfn
        self.__result = None

    def run(self):
        # Extract task-dependent params
        logfile_name = "log_" + str(self.params['msize']) + "_" + self.testfn.__name__
        logfile = open(os.path.join(SUBMITS, self.submit, logfile_name), "w+")

        submit_run = run(SUBMITS + self.submit, [str(self.params['msize'])],
                logfile = logfile)
        assert submit_run is not None

        msg = ""
        ret = -1

        # HERE starts a job run
        try:
            ret = self.testfn(submit_run, self.params['msize'])
        except RuntimeError as e:
            msg = "FAIL: %s" % str(e)
            pass
        submit_run.end()
        # HERE ends a job run

        if ret >= 0:
            msg = "OK: " + str(ret)
        self.__result = (ret, msg)

        logfile.write(msg)
        if logfile is not None: logfile.close()

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
            thread = threading.Thread(target = self.queue_runner, daemon=True)
            thread.start()
            threads.append(thread)

        for thread in threads:
            try:
                thread.join()
            except KeyboardInterrupt:
                pass


# Load tests

tests_module = __import__("tests")
tests = list(map(lambda x: getattr(tests_module, x), filter(lambda x: x.startswith("test_"),
    dir(tests_module))))

#memsizes = [1000, 2323, 3678
memsizes = [2048, 5000, 11247, 70000 # 2**17 + 47 
        ]
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

TestRunner(jobs, 4).run()

all_results = {}
for job in jobs:
    msize = job.params['msize']
    submit = job.submit
    
    mem_results.setdefault(msize, {})
    mem_results[msize].setdefault(submit,[None] * len(tests))

    mem_results[msize][submit][tests.index(job.testfn)] = job.get_result()

#for source in all_submits:
#    for msize in memsizes:
#        print("Memory size %d" % msize)
#        mem_results.setdefault(msize, {})
#        mem_results[msize].setdefault(source, [])
#        for test in tests:
#            clean(SUBMITS + source)
#            s = run(SUBMITS + source, [str(msize)])
#            sys.stdout.write("  %-40s" % str(test.__name__))
#            sys.stdout.flush()
#            res = -1
#            message = "OK"
#            try:
#                res = test(s, msize)
#            except RuntimeError as e:
#                message = "FAIL: %s" % str(e)
#
#            if res >= 0:
#                message = "OK: %d" % res
#                color = 'green'
#            else:
#                color = 'red'
#            
#            mem_results[msize][source].append((res, message))
#            print(colored(message,color))

# Format HTML output

html = open("results2.html", "w+")

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
    test_max = [0]*len(tests)
    for test in range(0,len(tests)):
        test_max[test] = 0
        for submit in submits:
            result = results[submit][test]
            if result:
                test_max[test] = max (test_max[test], result[0])

    # Test header
    html.write("<thead><tr><td>User</td>")
    for test in tests:
        html.write("<td>%s</td>"% test.__name__[5:])
    html.write("</tr></thead>\n")

    for submit in submits:
        html.write("<tr><td>%s</td>" % submit);
        for test in range(0,len(results[submit])):
            item = results[submit][test]
            if item:
                item0, item1 = item[0], item[1]
            else:
                item0, item1 = -1, "TIMEOUT/unknown error"
            if item0 == -1:
                sty = "background-color: red"
            else:
                if test_max[test] == item0:
                    sty = "background-color: lightgreen"
                else:
                    sty = "background-color: green"
            html.write("<td style=\"%s\"><div class=\"out\">%s</div></td>" %
                    (sty, escape(item1).replace("\n","<br/>\n")))
        html.write("</tr>\n")
    html.write("</table>")

html.write("Generated: %s</body></html>\n" % datetime.datetime.now().ctime())
html.close()

os.system('cp results2.html logs/results-`date -Iseconds`.html')

#if len(sys.argv) == 1:
    #os.system('scp results.html mino@ksp.sk:public_html/os/du2/')
    #os.system('scp results.html mino@ksp.sk:public_html/os/du2/results-`date -Iseconds`.html')
