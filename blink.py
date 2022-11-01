#!/usr/bin/python3

# for command loops
import time 
# for ip address validation
from ipaddress import ip_address
# for hostname/ip validation
import socket
#for connecting to mqtt - to install use "pip install paho-mqtt"
import paho.mqtt.client as paho
# for commandline, obvs
import cmd
# for debug
from pprint import PrettyPrinter
# for json debug
import json

broker=None

client = paho.Client("uic-001")

PP = PrettyPrinter(compact=True, width = 80, indent = 2, depth=10)

# client.subscribe("ucl/by-unid/+/+/OnOff")
# 
# client.subscribe("ucl/#")

def on_message(client, userdata, message):
    print(message.topic + " : " + message.payload.decode("ascii"))
    # print("received message: ", str(message.payload.decode("utf-8")))
    print("\r\n")

client.on_message=on_message

class TestShell(cmd.Cmd):
    intro = 'The uic client test shell. Type help or ? to list commands\n'
    prompt = '>'
    file = None
    
    # -- precommand
    def precmd(self, line):
        line = line.lower()
        return line

    # -- Basic Commands
    def do_connect(self, arg:str):
        'Connect to a host default=localhost: connect <host>'
        if arg == None:
            arg = input("host: ")
        PP.pprint(arg)
        connect(arg)

    def do_subscribe(self, arg):
        'Subscribe to topic: sub "mqtt/+/topic" '
        if arg == None:
            arg = input("topic:")
        PP.pprint(arg)
        res = subscribe(*parse(arg))
        print(res)
        #print("%s %s" %(res.topic, res.payload))

    def do_unsubscribe(self, arg):
        'Unsubscribe from topic: sub "mqtt/+/topic '
        if arg == None:
            arg = input("topic:")
        PP.pprint(arg)
        topic = unsubscribe(*parse(arg))

    def do_add(self, arg):
        'Add a node to the network: add <node-uid>'
        if arg == None:
            arg = input("psk:")
        PP.pprint(arg)
        add(*parse(arg))


    def do_remove(self, arg=None):
        'Remove a node from the network: remove [optional-euid]'
        if arg == None:
            remove()
        else:
            PP.pprint(arg)
            remove(*parse(arg))

    def do_toggle(self, arg):
        'Toggles an on/off endpoint: <node-euid>'
        if arg == None or len(arg) == 0:
            arg = input("uid:")
        PP.pprint(arg)
        arg = toggle(*parse(arg))

    def do_binsw(self, arg):
        'Turns a binary switch on (1) or off (0): binsw off'
        if arg == None:
            arg = input("uid:")
        PP.pprint(arg)
        arg = binsw(*parse(arg))

    def do_exit(self, s):
        'Exits this shell'
        return True

    def postcmd(self, stop, line):
        #print(f'postcmd({stop}, {line})')
        return cmd.Cmd.postcmd(self, stop, line)

    # -- Shutting down
    def postloop(self):
        print("goodbye!")
        client.loop_stop()
        client.disconnect()
        super(TestShell,self).postloop()


__default_host="127.0.0.1"

def __isIpAddr(addr: str):
    try:
        return True if type(ip_address(addr)) else False
    except ValueError:
        return False

def connect(arg):
    global broker
    global __default_host
    
    if arg and arg != __default_host:
        # there's potentially a host we want to connect to
        if __isIpAddr(arg):
            hst = arg
        else:
            hst = socket.gethostbyname(arg) # assume hostname
    else:
        # either arg is None or is set to our default host
        hst = __default_host

    if broker:
        # in the event we already have a broker...
        print("Already connected to: " + broker)
        choice = input("Disconnect and try again (Y/N)?")
        if choice.lower() == "y" or choice.lower() == "yes":
            client.loop_stop()
            client.disconnect()
            broker = hst
        else:
            return 0 #aborted disconnect
    else:
        broker = __default_host

    res = client.connect(broker)
    print("client.connect(" + broker + "): " + str(res))

    client.loop_start()

def subscribe(arg):
    res = client.subscribe(arg)
    print("client.subscribe(" + arg + "):" + str(res))
    return res

def unsubscribe(arg):
    res = client.unsubscribe(arg)
    print("client.unsubscribe(" + arg + "):" + str(res))
    return res

def binsw(arg=None):
    client.publish("ucl/by-unid/zw-CAE2476D-0002/ep0/OnOff/Commands/Toggle",'{}')

def toggle(arg=None):
    while(True):
        client.publish("ucl/by-unid/zw-CAE2476D-0002/ep0/OnOff/Commands/Toggle",'{}')
        time.sleep(.5)

def remove(arg=None):
    #ucl/by-unid/zw-E7E87210-0001/ProtocolController/NetworkManagement/Write : {"State":"remove node"}
    client.publish("ucl/by-unid/zw-E7E87210-0001/ProtocolController/NetworkManagement/Write", '{"State":"remove node"}')


# -- Parser
def parse(arg):
    return tuple(map(str, arg.split()))


if __name__ == '__main__':
    TestShell().cmdloop()

#while True:
#	client.publish("ucl/by-unid/zw-E7E87210-003/ep0/OnOff/Toggle","{}")
#	time.sleep(120)
