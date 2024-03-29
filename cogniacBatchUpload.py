#!/usr/bin/env python
"""
cogupload

A utility for robust parallel upload of media to Cogniac system.

usage:

cogupload <subject_uid> <directory_name> [-r]

Currently this is suitable for uploading to an 'input' subject since it does not set the consensus flag.

This uses 20 parallel upload threads with infinite retries on the media upload and associations.

Outputs for each item associated the media_id, size in Kb, and filename
"""

import cogniac
from cogniac.common import server_error
import os
import sys
from retrying import retry
from multiprocessing.pool import ThreadPool
from threading import Lock
from time import time

default_filetypes = ['bmp', 'jpg', 'avi', 'png', 'mp4', 'jpeg', 'mov']


def usage():
    print ("\nusage: cogupload <subject_uid> <directory> [-r]\n")
    print ("         -r:   recursive upload all media files under <directory>")
    sys.exit(1)


try:
    subject_uid = sys.argv[1]
    directory = sys.argv[2]
except:
    usage()


print ("Authenticating...")
cc = cogniac.CogniacConnection(timeout=60)
print (cc.tenant)

try:
    subject = cc.get_subject(subject_uid)
except:
    print("unable to get subject_uid %s" % subject_uid)
    usage()


if not os.path.isdir(directory):
    print("invalid directory", directory)
    usage()


output_lock = Lock()


def upload_and_associate(fn):
    if not os.path.isfile(fn) or fn.split('.')[-1].lower() not in default_filetypes:
        output_lock.acquire()
        print("skip", fn)
        output_lock.release()
        return 0

    sz = os.stat(fn).st_size

    @retry(wait_exponential_multiplier=200, wait_exponential_max=10000, retry_on_exception=server_error)
    def upload():
        media = cc.create_media(fn)
        return media

    media = upload()

    @retry(wait_exponential_multiplier=200, wait_exponential_max=10000, retry_on_exception=server_error)
    def associate():
        subject.associate_media(media, enable_wait_result=True, force_feedback=True)
        output_lock.acquire()
        print("%s %6d KB  %s" % (media, sz/1000, fn))
        output_lock.release()

    associate()
    return sz


if '-r' in sys.argv:
    files = []
    for root, subdirs, fnl in os.walk(directory):
        files.extend([root+'/'+fn for fn in fnl])
else:
    files = [directory + '/' + fn for fn in os.listdir(directory)]

pool = ThreadPool(24)

t0 = time()
results = pool.map(upload_and_associate, files)
dt = time()-t0

sumbytes = sum(results)

print("\nUploaded %d files to %s: %d bytes in %d seconds (%.1f mbps)" % (len(files), subject_uid, sumbytes, dt, 8*sumbytes/dt/1e6))
