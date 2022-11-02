#!/usr/bin/python3
# Usage: python blink.py
# Starts a command line program that can perform simple commands to a UnifySDK controller and devices
# Press ? for a list of commands

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

# globals
DEBUG = 9 # higher values print more debug messages
broker=None

__default_host="127.0.0.1"

HOMEID = ""

client = paho.Client("uic-001") # create the MQTT client

PP = PrettyPrinter(compact=True, width = 80, indent = 2, depth=10) #todo - get rid of this

# client.subscribe("ucl/by-unid/+/+/OnOff")
# 
# client.subscribe("ucl/#")

def on_message(client, userdata, message):
    'Messages from subscribed topics flow thru here'
    global HOMEID
    if DEBUG>5: print(message.topic + " : " + message.payload.decode("ascii"))
    if HOMEID == "": # searching for the HomeID - look in messages from Connect
        if "/State" in message.topic:
            homeid1=message.topic.split('/')
            for i in homeid1:
                if "zw-" in i:
                    homeid1=i
                    break
            nodeid = homeid1[-4:]
            homeid1=homeid1[:-4] # remove the NodeID
            if DEBUG>9: print(homeid1, nodeid)
            if int(nodeid)>1: # ignore HomeIDs that don't have any nodes attached
                HOMEID=homeid1
                client.unsubscribe("ucl/by-unid/+/State") # done with this so can now unsubscribe

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
        connect(arg)
        ProbeControllers()

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
        'Toggles an on/off endpoint forever: toggle <nodeID=0002>'
        if arg == None or len(arg) == 0:
            arg = input("uid:")
        PP.pprint(arg)
        arg = toggle(*parse(arg))

    def do_swon(self, arg):
        'Turns nodeID switch on: swon <nodeID=0002>'
        swon(*parse(arg))

    def do_swoff(self, arg):
        'Turns nodeID switch off: swoff <nodeID=0002>'
        swoff(*parse(arg))

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


def __isIpAddr(addr: str):
    try:
        return True if type(ip_address(addr)) else False
    except ValueError:
        return False

def connect(arg):
    'Connect to the MQTT broker assuming this is a UnifySDK'
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

    client.loop_start() # blocking

def subscribe(arg):
    res = client.subscribe(arg)
    print("client.subscribe(" + arg + "):" + str(res))
    return res

def unsubscribe(arg):
    res = client.unsubscribe(arg)
    print("client.unsubscribe(" + arg + "):" + str(res))
    return res

def swon(arg="0002"):
    if DEBUG>8:print(HOMEID, arg)
    client.publish("ucl/by-unid/" + HOMEID + arg + "/ep0/OnOff/Commands/On",'{}')

def swoff(arg="0002"):
    if DEBUG>8:print(HOMEID, arg)
    client.publish("ucl/by-unid/" + HOMEID + arg + "/ep0/OnOff/Commands/Off",'{}')

def toggle(arg="0002"):
    while(True):
        client.publish("ucl/by-unid/" + HOMEID + arg + "/ep0/OnOff/Commands/Toggle",'{}')
        time.sleep(.5)

def remove(arg=None):
    #ucl/by-unid/zw-E7E87210-0001/ProtocolController/NetworkManagement/Write : {"State":"remove node"}
    client.publish("ucl/by-unid/" + HOMEID + "-0001/ProtocolController/NetworkManagement/Write", '{"State":"remove node"}')

def ProbeControllers():
    res = client.subscribe("ucl/by-unid/+/State")
    print("probe")
    print(res)
    print("length=%d" % len(res))

# -- Parser
def parse(arg):
    return tuple(map(str, arg.split()))


if __name__ == '__main__':
    TestShell().cmdloop()

#while True:
#	client.publish("ucl/by-unid/zw-E7E87210-003/ep0/OnOff/Toggle","{}")
#	time.sleep(120)
