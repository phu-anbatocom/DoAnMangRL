#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink # Import TCLink để giới hạn băng thông

def create_bottleneck_topo():
    net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True, link=TCLink)

    print("INFO: *** Thêm Hosts ***")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    
    print("INFO: *** Thêm Switch ***")
    s1 = net.addSwitch('s1')
    
    print("INFO: *** Tạo Links ***")
    # Link h1-s1 không giới hạn
    net.addLink(h1, s1)
    
    # Link s1-h2 bị giới hạn băng thông còn 10 Mbps
    net.addLink(s1, h2, bw=10)

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_bottleneck_topo()