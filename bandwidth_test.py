#!/usr/bin/python
#test với mininet> h2 iperf -s & mininet> h1 iperf -c h2

from mininet.net import Mininet
# Chỉ cần import OVSKernelSwitch
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def run_bandwidth_test():
    net = None
    try:
        # 1. KHÔNG SỬ DỤNG Controller. 
        #    Xóa bỏ tham số controller=OVSController.
        net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True, link=TCLink, cleanup=True)

        print("INFO: *** Mạng sẽ hoạt động không cần Controller ***")

        print("INFO: *** Thêm Hosts ***")
        h1 = net.addHost('h1', ip='10.0.0.1/24')
        h2 = net.addHost('h2', ip='10.0.0.2/24')
        
        print("INFO: *** Thêm Switch ***")
        s1 = net.addSwitch('s1')
        
        print("INFO: *** Tạo Links ***")
        net.addLink(h1, s1)
        net.addLink(s1, h2, bw=10, delay='15ms')

        print("INFO: *** Bắt đầu Mạng ***")
        net.start()
        
        # 2. SAO CHÉP LOGIC TỪ static_routing.py VÀO ĐÂY
        print("\nINFO: *** Cài đặt flow rule để switch hoạt động như L2 switch ***")
        for sw in net.switches:
            # Lệnh này ra lệnh cho switch tự hoạt động như một learning switch
            sw.cmd('ovs-ofctl add-flow', sw.name, '"action=normal"')

        print("\nINFO: *** Chạy pingall để kiểm tra kết nối ban đầu ***")
        # Bây giờ pingall sẽ thành công
        net.pingAll()
        
        print("\nINFO: *** Dùng 'iperf' để đo băng thông. ***")
        CLI(net)

    finally:
        print("INFO: *** Dọn dẹp và dừng mạng ***")
        if net is not None:
            net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_bandwidth_test()