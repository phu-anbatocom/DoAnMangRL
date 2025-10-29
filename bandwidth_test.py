#!/usr/bin/python

from mininet.net import Mininet
# Thay đổi quan trọng: Import Controller và RemoteController
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

# --- ĐỊNH NGHĨA MỘT LEARNING SWITCH CONTROLLER BẰNG PYTHON ---
# Đây là một controller "in-process", nó chạy ngay trong kịch bản của bạn.
# Nó không cần bất kỳ file bên ngoài nào.
class LearningSwitch( Controller ):
    def __init__( self, name, **kwargs ):
        Controller.__init__( self, name, port=6633, **kwargs )
    def start( self ):
        # Lệnh 'ovs-ofctl' là một phần của gói 'openvswitch-switch'
        # và nó nên tồn tại. Chúng ta dùng nó để cài đặt một flow mặc định.
        self.cmd( 'ovs-ofctl del-flows s1' )
        self.cmd( 'ovs-ofctl add-flow s1 "action=normal"' )
# -----------------------------------------------------------

def run_bandwidth_test():
    net = None
    try:
        # 1. Chỉ định rõ chúng ta sẽ dùng controller tự định nghĩa
        net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True, link=TCLink,
                      controller=LearningSwitch, cleanup=True)

        print("INFO: *** Thêm một Controller Python nội bộ ***")
        # 2. Thêm controller 'c0' sử dụng lớp LearningSwitch của chúng ta
        c0 = net.addController('c0')
        
        # ... (phần còn lại của code giữ nguyên) ...
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
        
        print("INFO: *** Chạy pingall để xác minh kết nối ban đầu ***")
        net.pingAll()

        print("INFO: *** Dùng 'xterm h1 h2' và 'iperf' để đo băng thông. ***")
        
        CLI(net)

    finally:
        print("INFO: *** Dọn dẹp và dừng mạng ***")
        if net is not None:
            net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_bandwidth_test()