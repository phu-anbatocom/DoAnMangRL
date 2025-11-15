# minimal_test.py - Kịch bản kiểm tra tối giản

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time

class LinuxRouter(Node):
    """Một Node đã bật IP forwarding."""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')
    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MinimalTopo(Topo):
    """Topology đơn giản nhất: h1 <-> r1 <-> h2"""
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        r1 = self.addNode('r1', cls=LinuxRouter)
        self.addLink(h1, r1)
        self.addLink(h2, r1)

def run_minimal_test():
    topo = MinimalTopo()
    net = Mininet(topo=topo)
    
    try:
        net.start()

        info("--- Cấu hình mạng tối giản ---\n")
        h1, h2, r1 = net.get('h1', 'h2', 'r1')

        # Cấu hình h1
        h1.cmd('ifconfig h1-eth0 10.0.1.10/24 up')
        h1.cmd('route add default gw 10.0.1.1')

        # Cấu hình h2
        h2.cmd('ifconfig h2-eth0 10.0.2.10/24 up')
        h2.cmd('route add default gw 10.0.2.1')

        # Cấu hình router r1
        r1.cmd('ifconfig r1-eth0 10.0.1.1/24 up')
        r1.cmd('ifconfig r1-eth1 10.0.2.1/24 up')

        # Thêm một chút thời gian để các interface "ổn định"
        info("--- Chờ 2 giây để các interface ổn định ---\n")
        time.sleep(2)

        info("--- Thử nghiệm ping tự động từ Python --- (Dự kiến thất bại)\n")
        # Sử dụng cmdPrint để thấy output ngay lập tức
        h1.cmdPrint('ping -c 1 10.0.2.1')

        info("\n" + "="*50 + "\n")
        info("Bây giờ hãy thử ping thủ công trong CLI bên dưới.\n")
        info("Gõ lệnh: h1 ping -c 1 h2\n")
        info("="*50 + "\n")
        
        CLI(net)

    finally:
        info("*** Dọn dẹp và dừng Mininet ***\n")
        net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_minimal_test()