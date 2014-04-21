#!/usr/bin/env python
import sys
import signal
import urlparse
import hashlib
from boto.s3.connection import S3Connection 
import boto.exception
 
# ignore Ctrl+C
signal.signal(signal.SIGINT, lambda x,f: None)

def out(s):
    sys.stdout.write(s)
    sys.stdout.flush()
 
def read_request():
    lines = []
    while True:
        line = sys.stdin.readline()
        if line == "\n":
            return lines
        elif line == '':
            return None
        else:
            lines.append(line)
 
# parse "Key: Value" lines from apt into dictionary
def parse_options(lines):
    res = {}
    for line in lines:
        key, value = line.split(':', 1)
        res[key] = value.strip()
    return res
 
# send status message to apt
def status(uri, message):
    out("102 Status\nURI: %s\n" % uri)
    out("Message: %s\n" % message)
    out("\n\n")
 
# process "get file" command 
def acquire(args):
    uri = args['URI']
    filename = args['Filename']
    
    u = urlparse.urlparse('http://' + uri[5:])
    try:
        status(uri, "Connecting to S3")
        conn = S3Connection(u.username, u.password)
        bucket = conn.get_bucket(u.hostname)
        key = bucket.get_key(u.path)
        status(uri, "Retreiving S3 key")
        if key  is not None:
            out("100 URI Start\nURI: %s\n" % uri)
            out("Size: %d\n" % key.size)
            out("\n\n")
 
            def progress(bytes, total):
                status(uri, "Downloading: %d%%" % (100 * bytes/ total))
 
            key.get_contents_to_filename(filename, cb=progress, num_cb=10)
 
            # not sure if apt really needs all of them, but anyway
            sha256, sha1, md5 = hashlib.sha256(), hashlib.sha1(), hashlib.md5()
            with open(filename, 'r') as f:
                while True:
                    buf = f.read(10000000)
                    if buf == '':
                        break
                    else:
                        for h in (sha256, sha1, md5):
                            h.update(buf)
 
            out("201 URI Done\nURI: %s\n" % uri)
            out("Size: %d\n" % key.size)
            out("Filename: %s\n" % filename)
            out("MD5-Hash: %s\n" % md5.hexdigest())
            out("MD5Sum-Hash: %s\n" % md5.hexdigest())
            out("SHA1-Hash: %s\n" % sha1.hexdigest())
            out("SHA256-Hash: %s\n" % sha256.hexdigest())
            out("\n\n")
        else:
            out("400 URI Failure\nURI: %s\n" % uri)
            out("Message: Not Found\n")
            out("FailReason: HttpError404\n")
            out("\n\n")
    except boto.exception.S3ResponseError, e:
            out("400 URI Failure\nURI: %s\n" % uri)
            out("Message: %s %s" % (e.status, e.error_message))
            out("FailReason: %s" % e.reason)
            out("\n\n")
 
 
if __name__ == '__main__':
    out("100 Capabilities\n")
    out("Version: 1.1\n")
    out("Pipeline: true\n")
    out("Send-Config: true\n")
    out("\n\n")
 
    while True:
        req = read_request()
        if req is None:
            sys.exit(0)
        # not sure why, but apt sometimes sends extra newlines
        if req == []:  
            continue
        code = req[0].split()[0]
        if code == '600':
            acquire(parse_options(req[1:]))
