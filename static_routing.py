#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Host, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

class LinuxRouter(Host):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

def create_routing_topo():
    net = None
    try:
        # --- THAY ĐỔI 1: KHÔNG CÓ BẤT KỲ CONTROLLER NÀO ĐƯỢC ĐỊNH NGHĨA ---
        net = Mininet(switch=OVSKernelSwitch, autoSetMacs=True, cleanup=True)

        print("INFO: *** Mạng sẽ hoạt động không cần Controller ***")
        
        # ... (Phần tạo topo giữ nguyên) ...
        print("INFO: *** Thêm Routers ***")
        r1 = net.addHost('r1', cls=LinuxRouter, ip='10.0.1.1/24')
        r2 = net.addHost('r2', cls=LinuxRouter, ip='10.0.2.1/24')
        
        print("INFO: *** Thêm Hosts ***")
        h1 = net.addHost('h1', ip='10.0.1.100/24')
        h2 = net.addHost('h2', ip='10.0.2.100/24')
        
        print("INFO: *** Thêm Switches ***")
        s1, s2, s3 = [net.addSwitch(s) for s in ('s1', 's2', 's3')]

        print("INFO: *** Tạo Links ***")
        net.addLink(h1, s1); net.addLink(r1, s1)
        net.addLink(h2, s2); net.addLink(r2, s2)
        net.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth1',
                    params1={'ip': '192.168.1.1/24'}, params2={'ip': '192.168.1.2/24'})
        net.addLink(r1, s3, intfName1='r1-eth2', params1={'ip': '192.168.2.1/24'})
        net.addLink(r2, s3, intfName1='r2-eth2', params1={'ip': '192.168.2.2/24'})

        print("INFO: *** Bắt đầu Mạng ***")
        net.start()

        # --- THAY ĐỔI 2: CÀI ĐẶT FLOW RULES ĐỂ SWITCH TỰ HOẠT ĐỘNG ---
        print("\nINFO: *** Cài đặt flow rules để các switch hoạt động như L2 switch ***")
        for sw in net.switches:
            # Xóa các flow cũ (nếu có)
            sw.cmd('ovs-ofctl del-flows', sw.name)
            # Thêm flow rule 'action=normal'
            # 'normal' là một từ khóa đặc biệt của Open vSwitch, ra lệnh cho nó
            # hoạt động như một switch L2 learning truyền thống.
            sw.cmd('ovs-ofctl add-flow', sw.name, '"action=normal"')
        # -------------------------------------------------------------

        print("\nINFO: *** Cấu hình định tuyến tĩnh một cách tường minh ***")
        h1.cmd('ip route add default via 10.0.1.1')
        h2.cmd('ip route add default via 10.0.2.1')
        r1.cmd('ip route add 10.0.2.0/24 via 192.168.1.2 dev r1-eth1')
        r2.cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r2-eth1')
        
        print("\nINFO: *** Mạng đã sẵn sàng. Bắt đầu CLI. ***")
        print("*** Chạy 'pingall' để kiểm tra kết nối ban đầu. ***")
        net.pingAll()
        CLI(net)

    finally:
        print("INFO: *** Dọn dẹp và dừng mạng ***")
        if net is not None:
            net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_routing_topo()