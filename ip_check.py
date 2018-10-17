#!C:\Users\Bogdan.Polischuk\AppData\Local\Programs>Python

import os
import sys
import paramiko

class switch_1:
    def __init__(self):
        self.ip_range_text=[]
        self.error_ip = {}

    def add_ip(self, ip):
            self.ip_range_text.append(ip)

    def check_ip(self):
        ip_range_R = []

        for i in self.ip_range_text:
            temp_ip = i.split(".")
            if len(temp_ip) == 1:
                try:
                    test = temp_ip[1]
                    if test != False:
                        pass
                except IndexError:
                    break
            elif len(temp_ip) == 4:
                try:
                    o1 = int(temp_ip[0])
                    o2 = int(temp_ip[1])
                    o3 = int(temp_ip[2])
                    o4 = int(temp_ip[3])
                    if 0<=o1<255 and 0<=o2<255 and 0<=o3<255 and 0<=o4<255:
                        ip_range_R.append(i)
                    else:
                        self.error_ip[i] = "such IP not exist"
                except ValueError:
                    self.error_ip[i] = "this is not IP"
            else:
                self.error_ip[i] = "too long/short for IP"
        return ip_range_R


class In_Out_puT:
    def Input(self):
        ip = None
        while True:
            print('Input IP or press "Enter":')
            ip = input()
            sw.add_ip(ip)
            if len(ip) <= 1:
                print('check IP:')
                break

    def Output_error(self):
        return sw.error_ip



sw = switch_1()
In = In_Out_puT()
In.Input()
In.Output_error()

print(sw.check_ip())
#print(type(sw.check_ip()))
print(In.Output_error())
print(len(In.Output_error()))


class Session_SSH:
    def __init__(self):
        self.host = '0.0.0.0'
        self.user = 'Login'
        self.secret = 'Password'
        self.port = 22
        self.client = paramiko.SSHClient()
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def make_tunel(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.secret, port=self.port)

    def do_command(self, command):
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
        rez = '\n'.join(self.stdout.readlines())
        return rez

    def do_command_6250(self, command):
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
        rez = self.stdout.readlines()
        return rez

    def del_tunel(self):
        self.client.close()

class Manager:

    def __init__(self):
        self.inp_ip = sw.check_ip()

    def ping_com(self):
        com = {}
        for ip in self.inp_ip:
            com[ip] = "ping -c 2 -W 1 " + ip + " | grep '2 packet' | awk '{print $6}'"
        return com

    def vlan_com(self, ip_sw):
        com1 = {}
        for port in range(1, 25):
            com1[port] = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " SNMPv2-SMI::mib-2.17.7.1.4.5.1.1." + str(port) + " | awk '{ print $4 }'"
        return com1

    def vlan_com2(self, ip_sw):
        com15 = {}
        for port in range(1, 49):
            com15[port] = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " SNMPv2-SMI::mib-2.17.7.1.4.5.1.1." + str(port) + " | awk '{ print $4 }'"
        return com15

    def vlan_com6250(self, ip_sw):
        com20 = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " SNMPv2-SMI::enterprises.6486.800.1.2.1.3.1.1.2.1.1.3 | grep 'INTEGER: 1' | awk '{ print (substr($1,54,9))}'"
#        com20 = {}
#        for port in range(1001, 1025):
#            com20[port] = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " SNMPv2-SMI::enterprises.6486.800.1.2.1.3.1.1.2.1.1.3 | grep 'INTEGER: 1' | grep '" + str(port) + "' |  awk '{ print (substr($1,54,9))}'"
        return com20

    def type_com(self, ip_sw):
        com2 = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " .1.3.6.1.2.1.1.1 | grep STRING | awk '{ print $4 }'"
        return com2

    def deck_com_all(self, ip_sw, port):
        com_all = "snmpwalk -v 2c -c SNMPcomM " + ip_sw + " IF-MIB::ifAlias." + port + " | awk '{ print $4 }'"
        return com_all


man = Manager()
man.ping_com()


obj_ssh = Session_SSH()
obj_ssh.make_tunel()

for i in man.ping_com():
    test_ping = obj_ssh.do_command(man.ping_com()[i])
    if int(test_ping[0]) == 0:
        print(i, ' - ping OK!')
        man.type_com(i)
        typ = str(obj_ssh.do_command(man.type_com(i)))

        if typ == "S2326TP-EI\n":
            man.vlan_com(i)
            VLANS = {}
            for p in man.vlan_com(i):
                vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p+4))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p+4))))
                    # run function for deckription
                    print('HUAWEI(S2326TP-EI): Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan
        elif typ == "D-Link\n":
            man.vlan_com(i)
            VLANS = {}
            for p in man.vlan_com(i):
                vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                    # run function for deckription
                    print('D-Link: Ethernet-' + str(p) + ' -', vlan , ' Service description: ', desc)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan
        elif typ == "OmniStack\n":
            man.vlan_com(i)
            VLANS = {}
            for p in man.vlan_com(i):
                vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                    # run function for deckription
                    print('Alcatel 6224: Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan
        elif typ == "Alcatel-Lucent\n":
            man.vlan_com6250(i)
            snmp_ask = obj_ssh.do_command_6250(man.vlan_com6250(i))
            for c in snmp_ask:
                temp = c.split('.')
                vlan_a = temp[0]
                port_a = temp[1][0:4]
                if int(vlan_a) < 1101 and int(port_a) < 1025:
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, port_a)))
                    print('Alcatel 6250: Ethernet-' + str(int(temp[1][0:4]) - 1000) + ' -', temp[0],
                          ' Service description: ', desc)
        elif typ == "MES3500-24\n":
            man.vlan_com(i)
            VLANS = {}
            for p in man.vlan_com(i):
                vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                    # run function for deckription
                    print('ZyXEL MES3500-24: Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan
        elif typ == "S2352P-EI\n":
            man.vlan_com2(i)
            VLANS = {}
            for p in man.vlan_com2(i):
                vlan = int(obj_ssh.do_command(man.vlan_com2(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p + 4))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p + 4))))
                    # run function for deckription
                    print('HUAWEI(S2352P-EI): Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                    #print('HUAWEI(S2352P-EI): Ethernet-' + str(p) + ' -', vlan)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan
        elif typ == "S5300-28P-LI-AC\n":
            man.vlan_com(i)
            VLANS = {}
            for p in man.vlan_com(i):
                vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                if vlan < 1101:
                    man.deck_com_all(i, str(p + 4))
                    desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p + 4))))
                    # run function for deckription
                    #print('HUAWEI(S5300): GigabitEthernet-' + str(p) + ' -', vlan)
                    print('HUAWEI(S5300): Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                    VLANS[p] = vlan
                else:
                    VLANS[p] = vlan

    else:
        print(i, '- switch has problems or unavailable')


obj_ssh.del_tunel()

