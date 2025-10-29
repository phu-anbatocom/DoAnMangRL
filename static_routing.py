#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Host, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_routing_topo():
    net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True)

    # Thêm các host hoạt động như router
    print("INFO: *** Thêm Routers ***")
    r1 = net.addHost('r1', ip='10.0.1.1/24')
    r2 = net.addHost('r2', ip='10.0.2.1/24')
    
    print("INFO: *** Thêm Hosts ***")
    h1 = net.addHost('h1', ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', ip='10.0.2.100/24', defaultRoute='via 10.0.2.1')
    
    print("INFO: *** Thêm Switchs ***")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3') # Switch cho đường đi dự phòng

    print("INFO: *** Tạo Links ***")
    # Kết nối các host vào mạng
    net.addLink(h1, s1)
    net.addLink(r1, s1)
    net.addLink(h2, s2)
    net.addLink(r2, s2)
    
    # Đường đi chính (r1 <-> r2)
    net.addLink(r1, r2)
    
    # Đường đi dự phòng (r1 <-> s3 <-> r2)
    net.addLink(r1, s3)
    net.addLink(r2, s3)

    net.start()

    # Kích hoạt IP forwarding trên các router
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Cấu hình định tuyến tĩnh
    # h1 -> h2
    r1.cmd('ip route add 10.0.2.0/24 via 10.0.0.2 dev r1-eth1') # Đường chính
    r2.cmd('ip route add 10.0.1.0/24 via 10.0.0.1 dev r2-eth1') # Đường chính
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_routing_topo()