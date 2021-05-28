#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import sys

from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy

helpdoc = """
Simple script to test the API in command line
optionnal 1st arg : "inline" to get results as a single line, or "json" to get results as proper json
2nd arg           : method name
optionnal 3rd arg : "array" to mark following arguments are to be taken as elements of an array
following args    : method's arguments. To provide an array, write it as a string after "array", for instance : « array "['test','test2']" » or « array "[['test1','test2'],['test3','test4']]] ».
Examples from HCI root:
./hyphe_backend/test_client.py get_status
./hyphe_backend/test_client.py declare_page http://medialab.sciences-po.fr
./hyphe_backend/test_client.py declare_pages array "['http://medialab.sciences-po.fr','http://www.sciences-po.fr']"
./hyphe_backend/test_client.py inline store.get_webentities
"""


def display_message(message, other_lines=None, line_sep='*', side_sep='*', secondary=False, no_return=True):
    if secondary:
        line_sep = '-'
        side_sep = ''

    if not type(message) == list:
        message = [message]
    if not other_lines:
        other_lines = []
    if not type(other_lines) == list:
        other_lines = [[other_lines]]
    if (type(other_lines) == list) and (any([type(X) == str for X in other_lines])):
        other_lines = [other_lines]

    message = [message] + other_lines
    max_length = max([len(X) - 1 + sum(len(str(Y)) for Y in X) for X in message])

    # Printing
    print(line_sep * (max_length + 4))

    for message_line in message:
        line_length = sum([len(str(X)) for X in message_line]) + len(message_line) - 1
        diff_length = max_length - line_length
        line = side_sep + " "
        for messagePart in message_line:
            line += str(messagePart) + ' '
        line += " " * diff_length + side_sep
        print(line)
    print(line_sep * (max_length + 4))

    if no_return:
        return
    else:
        return message


def printValue(value):
    if inline == "json":
        print(json.dumps(value))
    elif inline:
        print(repr(value).decode("unicode-escape").encode('utf-8'))
    else:
        import pprint
        pprint.pprint(value)


def printError(error):
    print(' !! ERROR: ', error)


def shutdown(data):
    reactor.stop()


display_message('start')
print('argv', sys.argv)

auto_convert_integers = True
if '--no-convert-int' in sys.argv:
    sys.argv.remove('--no-convert-int')
    auto_convert_integers = False

if sys.argv[1] == "inline":
    inline = True
    startargs = 3
elif sys.argv[1] == "json":
    inline = "json"
    startargs = 3
else:
    inline = False
    startargs = 2

print('inline',inline,'startargs',startargs)


proxy = Proxy('http://127.0.0.1:6978')
command = sys.argv[startargs - 1]
args = []
is_array = False
for a in sys.argv[startargs:]:
    display_message(a)
    if a == "array":
        print('isarray')
        is_array = True
    else:
        print('else')
        if is_array:
            print('isarray')
            if (a.startswith('[') and a.endswith(']')) or (a.startswith('{') and a.endswith('}')):
                print('startswith')
                args.append(eval(a))
            elif not len(a):
                print('not len')
                args.append([])
            else:
                print('append [a]')
                args.append([a])
        elif a == "False" or a == "True":
            print('boolean weird convert')
            args.append(eval(a))
        else:
            if auto_convert_integers:
                try:
                    a = int(a)
                except:
                    pass
            print('append a')
            args.append(a)
        is_array = False

display_message('call args')
print(args)
re_clean_args = re.compile(r"^\[(.*)\]$")
if not inline:
    print("CALL:", command, re_clean_args.sub(r"\1", str(args)))
d = proxy.callRemote(command, *args)

d.addCallback(printValue).addErrback(printError)
d.addCallback(shutdown)
reactor.run()
