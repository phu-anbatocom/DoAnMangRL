#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_simple_topo():
    """Tạo một topo đơn giản: 1 switch, 3 hosts."""
    
    # 1. Khởi tạo Mininet. `switch=OVSKernelSwitch` là lựa chọn switch hiện đại.
    #    `autoSetMacs=True` để Mininet tự gán địa chỉ MAC.
    net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True)

    # 2. Thêm các node vào mạng
    print("INFO: *** Thêm Switch ***")
    s1 = net.addSwitch('s1')
    
    print("INFO: *** Thêm Hosts ***")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    # 3. Tạo các liên kết giữa các node
    print("INFO: *** Tạo Links ***")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    # 4. Bắt đầu mạng
    print("INFO: *** Bắt đầu Mạng ***")
    net.start()

    # 5. Mở giao diện dòng lệnh (CLI) để tương tác
    print("INFO: *** Chạy CLI ***")
    CLI(net)

    # 6. Dừng mạng khi thoát khỏi CLI
    print("INFO: *** Dừng Mạng ***")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_simple_topo()