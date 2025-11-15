# Toàn bộ file ospf_test.py - PHIÊN BẢN HOÀN CHỈNH CUỐI CÙNG
# Cần có FRR được cài đặt và cấu hình đúng trên hệ thống để chạy đoạn mã này.

import os
import time
import csv
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def cleanup_frr():
    info('*** Killing stale FRR processes\n'); os.system('sudo killall -9 zebra ospfd watchfrr staticd || true')
    info('*** Removing old FRR configs and runtime files\n'); os.system('sudo rm -rf /etc/frr/r*'); os.system('sudo rm -rf /tmp/frr')

class LinuxRouter(Node):
    def config(self, **params): super(LinuxRouter, self).config(**params); self.cmd('sysctl net.ipv4.ip_forward=1')
    def terminate(self): self.cmd('sysctl net.ipv4.ip_forward=0'); super(LinuxRouter, self).terminate()

class MyTestTopo(Topo):
    def build(self):
        for i in range(1, 6): self.addNode(f'r{i}', cls=LinuxRouter); self.addHost(f'h{i}')
        for i in range(1, 6): self.addLink(f'h{i}', f'r{i}', intfName1=f'h{i}-eth0', intfName2=f'r{i}-eth0')
        self.addLink('r1', 'r2', intfName1='r1-eth1', intfName2='r2-eth1'); self.addLink('r1', 'r3', intfName1='r1-eth2', intfName2='r3-eth1')
        self.addLink('r1', 'r4', intfName1='r1-eth3', intfName2='r4-eth1'); self.addLink('r1', 'r5', intfName1='r1-eth4', intfName2='r5-eth1')
        self.addLink('r2', 'r3', intfName1='r2-eth2', intfName2='r3-eth2'); self.addLink('r3', 'r4', intfName1='r3-eth3', intfName2='r4-eth2')

def run_ospf_simulation():
    cleanup_frr()
    topo = MyTestTopo()
    net = Mininet(topo=topo) 
    
    try:
        net.start()

        info("--- Cấu hình IP và Default Route cho Hosts ---\n")
        for i in range(1, 6): net.get(f'h{i}').cmd(f'ifconfig h{i}-eth0 10.0.{i}.10/24 up'); net.get(f'h{i}').cmd(f'route add default gw 10.0.{i}.1')
        info("--- Cấu hình IP cho các cổng Router ---\n")
        for i in range(1, 6): net.get(f'r{i}').cmd(f'ifconfig r{i}-eth0 10.0.{i}.1/24 up')
        net.get('r1').cmd('ifconfig r1-eth1 192.168.12.1/24 up'); net.get('r2').cmd('ifconfig r2-eth1 192.168.12.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth2 192.168.13.1/24 up'); net.get('r3').cmd('ifconfig r3-eth1 192.168.13.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth3 192.168.14.1/24 up'); net.get('r4').cmd('ifconfig r4-eth1 192.168.14.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth4 192.168.15.1/24 up'); net.get('r5').cmd('ifconfig r5-eth1 192.168.15.2/24 up')
        net.get('r2').cmd('ifconfig r2-eth2 192.168.23.1/24 up'); net.get('r3').cmd('ifconfig r3-eth2 192.168.23.2/24 up')
        net.get('r3').cmd('ifconfig r3-eth3 192.168.34.1/24 up'); net.get('r4').cmd('ifconfig r4-eth2 192.168.34.2/24 up')

        info("--- Cấu hình và khởi chạy FRR/OSPF ---\n")
        for i in range(1, 6):
            r = net.get(f'r{i}'); run_dir = f'/tmp/frr/r{i}'; conf_dir = f'/etc/frr/r{i}'; os.makedirs(run_dir, exist_ok=True); os.makedirs(conf_dir, exist_ok=True)
            os.system(f'sudo chown frr:frr {run_dir}'); os.system(f'sudo chown -R frr:frr {conf_dir}')
            
            with open(f'{conf_dir}/zebra.conf', 'w') as f: f.write(f'hostname r{i}\n')
            
            # --- PHẦN CẤU HÌNH OSPF ĐÚNG CHUẨN NHẤT ---
            with open(f'{conf_dir}/ospfd.conf', 'w') as f:
                f.write(f'hostname r{i}\n')
                f.write('router ospf\n')
                f.write(f' ospf router-id 1.1.1.{i}\n')
                # Bật OSPF trên TẤT CẢ các interface
                for intf in r.intfList():
                    if 'lo' not in intf.name:
                        f.write(f'interface {intf.name}\n')
                        # Nếu là interface nối router-router, chỉ định là point-to-point
                        if intf.name != f'r{i}-eth0':
                            f.write(' ip ospf network point-to-point\n')
                        f.write(' ip ospf area 0\n')
            # --- KẾT THÚC PHẦN THAY ĐỔI ---

            r.cmd(f'/usr/lib/frr/zebra -d -f {os.path.abspath(conf_dir)}/zebra.conf -z {os.path.abspath(run_dir)}/zebra.api -i {os.path.abspath(run_dir)}/zebra.pid')
            time.sleep(1)
            r.cmd(f'/usr/lib/frr/ospfd -d -f {os.path.abspath(conf_dir)}/ospfd.conf -z {os.path.abspath(run_dir)}/zebra.api -i {os.path.abspath(run_dir)}/ospfd.pid')

        info("--- Chờ OSPF hội tụ (60 giây) ---\n")
        time.sleep(60)
        # Có vẻ thời gian chờ không liên quan đến hội tụ
        # Thay vào đó, cần ping từng đôi host để mồi cho bảng routing được xây dựng đúng
        
        info("\n*** Mở CLI để Debug. ***\n")
        CLI(net)

        # Hiện tại cần ping từng đôi host để mồi cho pingall hoạt động đúng
        # Kể cả khi đó, tỉ lệ drop vẫn ở 50% do router không thể được ping trực tiếp

    finally:
        info("--- Dọn dẹp và dừng Mininet ---\n")
        net.stop()
        cleanup_frr()

if __name__ == '__main__':
    setLogLevel('info')
    run_ospf_simulation()