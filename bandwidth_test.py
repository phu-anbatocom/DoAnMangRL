#!/usr/bin/python

from mininet.net import Mininet # type: ignore
from mininet.node import OVSKernelSwitch # type: ignore
from mininet.cli import CLI # type: ignore
from mininet.log import setLogLevel # type: ignore
from mininet.link import TCLink # type: ignore # Import TCLink để giới hạn băng thông

def run_bandwidth_test():
    """
    Tạo topo có nút cổ chai, chạy CLI, và đảm bảo dọn dẹp an toàn.
    """
    # 1. Khởi tạo biến 'net' là None. 
    #    Điều này để đảm bảo chương trình không bị lỗi nếu việc tạo Mininet thất bại.
    net = None
    try:
        # --- Khối code chính nằm trong 'try' ---
        
        # 2. Tạo đối tượng Mininet. 
        #    'cleanup=True' là một tùy chọn hữu ích để tự động dọn dẹp khi bắt đầu.
        net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True, link=TCLink, cleanup=True)

        print("INFO: *** Thêm Hosts ***")
        h1 = net.addHost('h1', ip='10.0.0.1/24')
        h2 = net.addHost('h2', ip='10.0.0.2/24')
        
        print("INFO: *** Thêm Switch ***")
        s1 = net.addSwitch('s1')
        
        print("INFO: *** Tạo Links ***")
        # Link h1-s1 không giới hạn
        net.addLink(h1, s1)
        
        # Link s1-h2 bị giới hạn băng thông còn 10 Mbps và có độ trễ 15ms
        print("INFO: *** Tạo nút cổ chai (10Mbps, 15ms delay) ***")
        net.addLink(s1, h2, bw=10, delay='15ms')

        print("INFO: *** Bắt đầu Mạng ***")
        net.start()
        
        print("INFO: *** Chạy CLI. Dùng 'xterm h1 h2' và 'iperf' để kiểm tra. ***")
        CLI(net)

    finally:
        # --- Khối 'finally' LUÔN LUÔN được thực thi ---
        print("INFO: *** Dọn dẹp và dừng mạng ***")
        # 3. Kiểm tra xem đối tượng 'net' đã được tạo thành công chưa trước khi dừng nó.
        if net is not None:
            net.stop()

if __name__ == '__main__':
    # Đặt mức độ log để thấy các thông báo INFO
    setLogLevel('info')
    run_bandwidth_test()