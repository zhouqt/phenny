#!/usr/bin/env python
"""
tools.py - Phenny Tools
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""


def deprecated(old):
    def new(phenny, input_msg, old=old):
        self = phenny
        origin = type('Origin', (object,), {
                      'sender': input_msg.sender,
                      'nick': input_msg.nick
                      })()
        match = input_msg.match
        args = [input_msg.msg_bytes, input_msg.sender, '@@']

        old(self, origin, match, args)
    new.__module__ = old.__module__
    new.__name__ = old.__name__
    return new

if __name__ == '__main__':
    print __doc__.strip()
