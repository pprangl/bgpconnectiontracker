# b'16:13:45.978841 98:5d:82:a2:73:fd (oui Arista Networks) > 28:99:3a:33:a4:59 (oui Arista Networks), ethertype IPv4 (0x0800), length 85: (tos 0xc0, ttl 1, id 36897, offset 0, flags [DF], proto TCP (6), length 71)'
# b'    10.0.0.2.bgp > 10.0.0.1.40221: Flags [P.], seq 1:20, ack 19, win 509, options [nop,nop,TS val 1068892832 ecr 1621776562], length 19: BGP'
# b'\tKeepalive Message (4), length: 19'

import subprocess as sub
import re
from datetime import datetime, timedelta, time
from jsonrpclib import Server
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

ipAddr = []
macAddr = []
connections = []
macConnections = []
timestamp = ''
timestamps = []
loopCount = 0
interfaces = ['Ethernet 15/1', 'Ethernet15/2', 'Ethernet15/3']

p = sub.Popen(('sudo', 'tcpdump', '-l', 'tcp port 179', '--interface=mirror0', '-vvs0'), stdout=sub.PIPE)
for row in iter(p.stdout.readline, b''):
    if re.findall(r'((\w+):+)+\w+ \(', row.strip().decode()):
        macAddr = re.findall(r'(?:\w+:)+\w+ ', row.strip().decode())
    if re.findall(r'\d+:\d+:\d+.\d+ ', row.strip().decode()):
        timestamp = re.findall(r'\d+:\d+:\d+.\d+ ', row.strip().decode())
        # print(timestamp[0])
        loopCount += 1
    if re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}.(bgp)*(\d)*', row.strip().decode()):
        ipAddr = re.findall(r'((?:[0-9]{1,3}\.){3}[0-9]{1,3}.(bgp)*(\d)*)', row.strip().decode())
        loopCount += 1
    if 'Keepalive Message (4)' in row.strip().decode():
        print('KeepAlive Session from ' + ipAddr[0][0] + ' to ' + ipAddr[1][0] + ' was found!')
        print('KeepAlive Session from ' + macAddr[0].replace(' ','') + ' to ' + macAddr[1].replace(' ','') + ' was found!')
        conn = {ipAddr[0][0]: ipAddr[1][0]}
        connMacs = {macAddr[0].replace(' ','') : macAddr[1].replace(' ', '')}
        keyMatch = False
        valueMatch = False
        if len(connections) > 0:
            for d in connections:
                # print(d)
                for key, value in d.items():
                    if key == ipAddr[0][0]: # or key == ipAddr[1][0]:
                        keyMatch = True
                    if value == ipAddr[1][0]: # or value == ipAddr[0][0]:
                        valueMatch = True
            if keyMatch == False and valueMatch == False:
                connections.append(conn)
                timestamps.append(timestamp[0].replace(" ", ""))
                macConnections.append(connMacs)
            elif keyMatch == True and valueMatch == True:
                ind = connections.index(conn)
                timestamps[ind] = timestamp[0].replace(" ", "")
        else:
            connections.append(conn)
            timestamps.append(timestamp[0].replace(" ", ""))
            macConnections.append(connMacs)
        loopCount += 1
    if loopCount == 3:
        twoHours = datetime.now()  - timedelta(hours = 2)
        for stamp in timestamps:
            # print(stamp)
            sp = stamp.split('.')
            h,m,s = sp[0].split(':')
            dat = time(hour=int(h),minute=int(m),second=int(s),microsecond=int(sp[1]))
            if dat > twoHours.time():
                print("Timestamp newer than two hours")
        trafficPolicyBegin = ['traffic-policies', 'traffic-policy ISPA', 'match bgp_in ipv4', 'protocol tcp source port bgp destination port all',\
                              'match bgp_out ipv4', 'protocol tcp source port all destination port bgp']
        trafficPolicyMid = []
        trafficPolicyEnd = ['match ipv4-all-default ipv4', 'actions', 'drop', 'match ipv6-all-default ipv6', 'actions', 'drop']
        seq = 10
        for macConnection in macConnections:
            for key, value in macConnection.items():
                matchStatement = 'match ' + str(seq) + ' mac'
                sourceMACPolicy = 'source mac ' + str(key)
                destinationMACPolicy = 'destination mac ' + str(value)
                trafficPolicyMid.extend([matchStatement, sourceMACPolicy, destinationMACPolicy])
                seq += 10
        trafficPolicy = trafficPolicyBegin + trafficPolicyMid + trafficPolicyEnd
        switch = Server("https://test:test@127.0.0.1/command-api")
        cmdList = ["enable",
              "configure"]
        for item in trafficPolicy:
            cmdList.append(item)
        for intf in interfaces:
            cmdList.append('interface ' + intf)
            cmdList.append('traffic-policy input ISPA')
        print(cmdList)
        response = switch.runCmds( 1, cmdList )
        # print("Hello, my name is: ", response[0])
        loopCount = 0
