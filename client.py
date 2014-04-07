#!/usr/bin/env python
import fileinput
import os
import sys
import json
import urllib2
import codecs
from urllib import urlencode
from urlparse import urlsplit, urlunsplit
from optparse import OptionParser


def create_paste(opts, filename):
    u = urlsplit(opts.url)
    query = urlencode([('key', opts.key), ('guess', opts.guess)])
    url = urlunsplit((u[0], u[1], u[2], query, u[4]))

    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')

    if filename == '-':
        content = sys.stdin.read()
    else:
        content = codecs.open(filename, 'r', encoding='utf-8').read()

    data = {
        'name': opts.name or u"",
        'expire_on': opts.expire or u'1hr',
        'syntax': opts.syntax,
        'content': content,
    }

    response = urllib2.urlopen(request, json.dumps(data))
    if response.getcode() != 201:
        print "ERROR: %d" % response.getcode()
        print response.info()
        rv = 1
    else:
        response_data = json.load(response)
        print "Paste %(paste_id)s created at %(link)s" % response_data['paste']
        rv = 0
    sys.exit(rv)

def main():
    parser = OptionParser(description="pasticcio client")
    parser.add_option('-U', '--url', default='http://127.0.0.1:5000/api/paste/',
                      help="Specify the HTTP endpoint")
    parser.add_option('-K', '--key', help="Specify an API key")
    parser.add_option('-n', '--name', help="Set the paste name")
    parser.add_option('-x', '--expire', help="Set the expiration time",
                      choices=('never', '1hr', '1d', '1w', '1M'))
    parser.add_option('-s', '--syntax', default='text',
                      help="Set the paste syntax")
    parser.add_option('-g', '--guess', action='store_true',
                      help="Turn on syntax guessing")
    
    (opts, args) = parser.parse_args()

    key = opts.key or os.environ.get('PASTICCIO_KEY')
    url = opts.url or os.environ.get('PASTICCIO_URL')

    if not url or not key:
        parser.error("You must specify an API key and a HTTP endpoint.\n"
                     "See option -K and -U or PASTICCIO_KEY and PASTICCIO_URL.")
    if not args:
        parser.error("You must specify one target filename")

    create_paste(opts, args[0])

if __name__ == '__main__':
    main()
