#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_simple_topo():
    """Tạo một topo đơn giản và đảm bảo dọn dẹp."""
    
    net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True)

    print("INFO: *** Thêm Switch ***")
    s1 = net.addSwitch('s1')
    
    print("INFO: *** Thêm Hosts ***")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    print("INFO: *** Tạo Links ***")
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    print("INFO: *** Bắt đầu Mạng ***")
    net.start()

    print("INFO: *** Chạy CLI ***")
    CLI(net)

    print("INFO: *** Dừng Mạng ***")
    net.stop() # Lệnh net.stop() chính là lệnh dọn dẹp cho topo hiện tại

if __name__ == '__main__':
    setLogLevel('info')
    
    # Sử dụng try...finally
    network = None # Khởi tạo để tránh lỗi nếu net chưa được tạo
    try:
        # Đoạn code chính nằm ở đây. 
        # Chúng ta không gọi trực tiếp create_simple_topo() nữa, 
        # mà sẽ xây dựng mạng ngay trong khối try.
        
        network = Mininet(switch=OVSKernelSwitch, autoSetMacs=True)
        s1 = network.addSwitch('s1')
        h1 = network.addHost('h1')
        h2 = network.addHost('h2')
        network.addLink(h1, s1)
        network.addLink(h2, s1)
        network.start()
        
        CLI(network)

    finally:
        # Khối này LUÔN LUÔN được chạy
        print("INFO: *** Đang dọn dẹp và dừng mạng ***")
        if network is not None:
            network.stop()