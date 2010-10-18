import sys
import os
import signal
import subprocess
import time
import twill
import urllib2
import os.path
import re

TEST_PATH = os.path.dirname(os.path.abspath(__file__))

def waitforport(port, start):
    while True:
        if time.time() - start > 900:
            raise Exception('Servers did not start in 90 seconds')
        time.sleep(1)
        try:
            urllib2.urlopen('http://localhost:%s' % port)
        except urllib2.URLError:
            continue
        else:
            break

pids = []

def setup():
    idp_command = ['python', os.path.join(TEST_PATH, 'idp_manage.py'), 'runserver', 'localhost:10000', '--verbosity=2']
    p = subprocess.Popen(idp_command)
    pids.append(p.pid)

    sp_command = ['python', os.path.join(TEST_PATH, 'sp_manage.py'), 'runserver', 'localhost:10001', '--verbosity=2']
    p = subprocess.Popen(sp_command)
    pids.append(p.pid)

    # Wait for the daemons to load themselves
    starttime = time.time()
    waitforport(10000, starttime)
    waitforport(10001, starttime)

def teardown():
    for pid in pids:
        try:
            # TODO: do something better...
            if os.path.exists("/proc/" + str(pid+2)):
                os.kill(pid+2, signal.SIGINT) # In status check the Ppid
            os.kill(pid, signal.SIGINT)
        except OSError:
            print >> sys.stderr, 'failed to kill pid %s or its son' % pid
