#!/usr/bin/env python
"""
chat.py - Phenny Chatbot Module

Author: Qingtang Zhou <qzhou@redhat.com>
"""

import urllib
import random
import re
from HTMLParser import HTMLParser


PANDORABOTS_API = "http://www.pandorabots.com/pandora/talk-xml"

PANDORABOTS_ID = "8ec716178e3493ef"
ALICE_ID = "f5d922d97e345aa1"

OOPS = "OOPS! My head is stolen by ET!"

CHAT_SESSIONS = {}

_unescape = HTMLParser().unescape

def chat(phenny, input_msg):
    words = input_msg.group(1)

    if re.findall(ur'[\u4e00-\u9fff]+', words):
        return phenny.reply(OOPS)

    nick = input_msg.nick.lower()
    if nick not in CHAT_SESSIONS.keys():
        custid = '%016x' % random.getrandbits(64)
        CHAT_SESSIONS[nick] = custid
    else:
        custid = CHAT_SESSIONS.get(nick)

    post_data = {"botid": PANDORABOTS_ID,
                 "custid": custid,
                 "input": words
                }
    post_data = urllib.urlencode(post_data)
    reply_data = urllib.urlopen(PANDORABOTS_API, post_data).read()
    if custid not in reply_data:
        return phenny.reply(OOPS)

    if not re.search("""status=['"]*0""", reply_data):
        return phenny.reply(OOPS)

    reply_msg = re.findall("""<that>(.*?)</""", reply_data)
    if not reply_msg:
        return phenny.reply(OOPS)

    formated_msg = _unescape(str(reply_msg[0]))
    formated_msg = re.sub("\<br.*?\>", "", formated_msg)
    return phenny.reply(formated_msg)
chat.name = 'chat'
chat.rule = ("$nick", r"(.*)")
chat.priority = 'low'

if __name__ == '__main__':
   print __doc__.strip()
