import json
import re
from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy

version_build = "0.2"
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

command_array = ['store.simulate_creationrules_for_urls', 'https://www.nouvelobs.com/,https://www.lemonde.fr',
                 'test_script_auto']
inline = False
startargs = 2
command = command_array[0]


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


proxy = Proxy('http://127.0.0.1:6978')
args = []
is_array = False
for a in command_array[startargs:]:
    if a == "array":
        is_array = True
    if is_array:
        if (a.startswith('[') and a.endswith(']')) or (a.startswith('{') and a.endswith('}')):
            args.append(eval(a))
        elif not len(a):
            args.append([])
        else:
            args.append([a])
    elif a == "False" or a == "True":
        args.append(eval(a))
    else:
        if auto_convert_integers:
            try:
                a = int(a)
            except:
                pass
        args.append(a)
    is_array = False

re_clean_args = re.compile(r"^\[(.*)\]$")
if not inline:
    print("CALL:", command, re_clean_args.sub(r"\1", str(args)))
d = proxy.callRemote(command, *args)

d.addCallback(printValue).addErrback(printError)
d.addCallback(shutdown)
reactor.run()
