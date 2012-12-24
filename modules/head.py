#!/usr/bin/env python
"""
head.py - Phenny HTTP Metadata Utilities
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import urllib2
import httplib
import urlparse
import time
import sys
from htmlentitydefs import name2codepoint
import web


def head(phenny, input_msg):
   """Provide HTTP HEAD information."""
   uri = input_msg.group(2)
   uri = (uri or '').encode('utf-8')
   if ' ' in uri:
      uri, header = uri.rsplit(' ', 1)
   else: uri, header = uri, None

   if not uri and hasattr(phenny, 'last_seen_uri'):
      try: uri = phenny.last_seen_uri[input_msg.sender]
      except KeyError: return phenny.say('?')

   if not uri.startswith('htt'):
      uri = 'http://' + uri
   # uri = uri.replace('#!', '?_escaped_fragment_=')

   try: info = web.head(uri)
   except IOError: return phenny.say("Can't connect to %s" % uri)
   except httplib.InvalidURL: return phenny.say("Not a valid URI, sorry.")

   if not isinstance(info, list):
      try: info = dict(info)
      except TypeError:
         return phenny.reply('Try .head http://example.org/ [optional header]')
      info['Status'] = '200'
   else:
      newInfo = dict(info[0])
      newInfo['Status'] = str(info[1])
      info = newInfo

   if header is None:
      data = []
      if info.has_key('Status'):
         data.append(info['Status'])
      if info.has_key('content-type'):
         data.append(info['content-type'].replace('; charset=', ', '))
      if info.has_key('last-modified'):
         modified = info['last-modified']
         modified = time.strptime(modified, '%a, %d %b %Y %H:%M:%S %Z')
         data.append(time.strftime('%Y-%m-%d %H:%M:%S UTC', modified))
      if info.has_key('content-length'):
         data.append(info['content-length'] + ' msg_bytes')
      phenny.reply(', '.join(data))
   else:
      headerlower = header.lower()
      if info.has_key(headerlower):
         phenny.say(header + ': ' + info.get(headerlower))
      else:
         msg = 'There was no %s header in the response.' % header
         phenny.say(msg)
head.commands = ['head']
head.example = '.head http://www.w3.org/'

r_title = re.compile(r'(?ims)<title[^>]*>(.*?)</title\s*>')
r_entity = re.compile(r'&[A-Za-z0-9#]+;')


def __escape(m):
    entity = m.group(0)
    if entity.startswith('&#x'):
       cp = int(entity[3:-1], 16)
       return unichr(cp).encode('utf-8')
    elif entity.startswith('&#'):
       cp = int(entity[2:-1])
       return unichr(cp).encode('utf-8')
    else:
       char = name2codepoint[entity[1:-1]]
       return unichr(char).encode('utf-8')


def do_get_title(phenny, uri):
    blacklist = [
       'https?://localhost/',
       'https?://localhost:\d+/',
       'https?://127.0.0.1/',
       'https?://127.0.0.1:\d+/',
    ]
    if hasattr(phenny.config, "get_title_blacklist"):
        blacklist += phenny.config.get_title_blacklist

    for entry in blacklist:
        if re.search(entry, uri):
            print >> sys.stderr, "uri is in blacklist"
            return False, ""

    redirects = 0
    while True:
        headers = {
           'Accept': 'text/html',
           'User-Agent': 'Mozilla/5.0 (Phenny)'
        }
        req = urllib2.Request(uri, headers=headers)
        try:
            u = urllib2.urlopen(req)
            info = u.info()
            u.close()
        except IOError, e:
            err_msg = ""
            try:
                if e.getcode() > 400:
                    err_msg = "%s - %s" % (e.getcode(), e.reason)
            except Exception:
                pass
            print >> sys.stderr, e
            return False, err_msg
        # info = web.head(uri)

        if not isinstance(info, list):
            status = '200'
        else:
            status = str(info[1])
            info = info[0]
        if status.startswith('3'):
            uri = urlparse.urljoin(uri, info['Location'])
        else:
            break

        redirects += 1
        if redirects >= 25:
            print >> sys.stderr, "Too many redirection"
            return False, ""

    try:
        mtype = info['content-type']
    except Exception:
        print >> sys.stderr, "Can't find content tyep"
        return False, ""

    if not (('/html' in mtype) or ('/xhtml' in mtype)):
        print >> sys.stderr, "Document isn't html"
        return False, ""

    try:
        u = urllib2.urlopen(req)
        msg_bytes = u.read(262144)
        u.close()
    except IOError, e:
        print type(e), e
        print >> sys.stderr, "Can't connect to %s, err = %s" % (uri, e)
        return False, ""

    m = r_title.search(msg_bytes)
    if not m:
        print >> sys.stderr, "No title in document"
        return False, ""

    title = m.group(1)
    title = title.strip()
    title = title.replace('\t', ' ')
    title = title.replace('\r', ' ')
    title = title.replace('\n', ' ')
    while '  ' in title:
        title = title.replace('  ', ' ')
    if len(title) > 200:
        title = title[:200] + '[...]'

    title = r_entity.sub(__escape, title)

    if not title:
        return False, "[The title is empty.]"

    enc_list = ("utf-8", "cp936", "iso-8859-1", "cp1252")
    try:
        title.decode('utf-8')
    except Exception:
        for enc in enc_list:
            try:
                title = title.decode(enc).encode('utf-8')
                break
            except Exception:
                continue
        else:
            return False, "[Unknown title encode.]"

    title = title.replace('\n', '')
    title = title.replace('\r', '')
    return True, title


def title(phenny, input_msg):
    """.title <URI> - Return the title of URI."""
    uri = input_msg.group(1)
    uri = (uri or '').encode('utf-8')

    if not uri and hasattr(phenny.bot, 'last_seen_uri'):
       uri = phenny.bot.last_seen_uri.get(input_msg.sender)
    if not uri:
       return phenny.reply('I need a URI to give the title of...')

    if not ':' in uri:
       uri = 'http://' + uri
    uri = uri.replace('#!', '?_escaped_fragment_=')

    ret, msg = do_get_title(phenny, uri)
    if not ret:
        if msg:
            return phenny.reply(msg)
        return
    return phenny.say("TITLE: %s" % msg)
title.commands = ['title']


def get_title(phenny, input_msg):
    uri = input_msg.group(1).encode("utf-8")
    ret, msg = do_get_title(phenny, uri)
    if not ret:
        if msg:
            return phenny.reply(msg)
        return
    return phenny.say("TITLE: %s" % msg)
get_title.rule = r'.*(https?://[^<> "\x01]+)[,.]?'
get_title.priority = 'low'
get_title.last_cmd = True


def noteuri(phenny, input_msg):
   uri = input_msg.group(1).encode('utf-8')
   if not hasattr(phenny.bot, 'last_seen_uri'):
      phenny.bot.last_seen_uri = {}
   phenny.bot.last_seen_uri[input_msg.sender] = uri
noteuri.rule = r'.*(http[s]?://[^<> "\x01]+)[,.]?'
noteuri.priority = 'low'
noteuri.last_cmd = True

if __name__ == '__main__':
   print __doc__.strip()
