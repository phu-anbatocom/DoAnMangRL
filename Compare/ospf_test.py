# Toàn bộ file ospf_test.py - PHIÊN BẢN HOÀN CHỈNH, TỰ ĐỘNG, ĐÁNG TIN CẬY

import os
import time
import csv
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink
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
        for i in range(1, 6): self.addLink(f'h{i}', f'r{i}', intfName1=f'h{i}-eth0', intfName2=f'r{i}-eth0', cls=TCLink, bw=100)
        self.addLink('r1', 'r2', intfName1='r1-eth1', intfName2='r2-eth1', cls=TCLink, bw=50, delay='5ms')
        self.addLink('r1', 'r3', intfName1='r1-eth2', intfName2='r3-eth1', cls=TCLink, bw=50, delay='5ms')
        self.addLink('r1', 'r4', intfName1='r1-eth3', intfName2='r4-eth1', cls=TCLink, bw=50, delay='5ms')
        self.addLink('r1', 'r5', intfName1='r1-eth4', intfName2='r5-eth1', cls=TCLink, bw=50, delay='5ms')
        self.addLink('r2', 'r3', intfName1='r2-eth2', intfName2='r3-eth2', cls=TCLink, bw=20, delay='10ms')
        self.addLink('r3', 'r4', intfName1='r3-eth3', intfName2='r4-eth2', cls=TCLink, bw=20, delay='10ms')

def parse_iperf(iperf_output):
    lines = iperf_output.strip().split('\n'); last_line = lines[-1]
    if 'Mbits/sec' in last_line: return float(last_line.split()[-2])
    elif 'Gbits/sec' in last_line: return float(last_line.split()[-2]) * 1000
    elif 'Kbits/sec' in last_line: return float(last_line.split()[-2]) / 1000.0
    return 0.0

def parse_ping(ping_output):
    avg_latency = 0.0; packet_loss = 100.0
    for line in ping_output.split('\n'):
        if 'packet loss' in line:
            try: packet_loss = float(line.split(',')[2].strip().split('%')[0])
            except: pass
        if 'rtt min/avg/max/mdev' in line:
            try: avg_latency = float(line.split('=')[1].strip().split('/')[1])
            except: pass
    return avg_latency, packet_loss

def run_ospf_simulation():
    cleanup_frr()
    topo = MyTestTopo()
    net = Mininet(topo=topo, link=TCLink) 
    
    try:
        net.start()
        info("*** Waiting for TCLinks to be fully initialized (3 seconds)... ***\n"); time.sleep(3)

        info("--- Configuring IP addresses and routes ---\n")
        for i in range(1, 6):
            net.get(f'h{i}').cmd(f'ifconfig h{i}-eth0 10.0.{i}.10/24 up'); net.get(f'h{i}').cmd(f'route add default gw 10.0.{i}.1')
            net.get(f'r{i}').cmd(f'ifconfig r{i}-eth0 10.0.{i}.1/24 up')
        net.get('r1').cmd('ifconfig r1-eth1 192.168.12.1/24 up'); net.get('r2').cmd('ifconfig r2-eth1 192.168.12.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth2 192.168.13.1/24 up'); net.get('r3').cmd('ifconfig r3-eth1 192.168.13.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth3 192.168.14.1/24 up'); net.get('r4').cmd('ifconfig r4-eth1 192.168.14.2/24 up')
        net.get('r1').cmd('ifconfig r1-eth4 192.168.15.1/24 up'); net.get('r5').cmd('ifconfig r5-eth1 192.168.15.2/24 up')
        net.get('r2').cmd('ifconfig r2-eth2 192.168.23.1/24 up'); net.get('r3').cmd('ifconfig r3-eth2 192.168.23.2/24 up')
        net.get('r3').cmd('ifconfig r3-eth3 192.168.34.1/24 up'); net.get('r4').cmd('ifconfig r4-eth2 192.168.34.2/24 up')

        info("--- Applying permissive firewall rules to all routers ---\n")
        for i in range(1, 6):
            r = net.get(f'r{i}'); r.cmd('iptables -F'); r.cmd('iptables -A INPUT -j ACCEPT'); r.cmd('iptables -A FORWARD -j ACCEPT'); r.cmd('iptables -A OUTPUT -j ACCEPT')

        info("--- Configuring and starting FRR/OSPF ---\n")
        for i in range(1, 6):
            r = net.get(f'r{i}'); run_dir = f'/tmp/frr/r{i}'; conf_dir = f'/etc/frr/r{i}'; os.makedirs(run_dir, exist_ok=True); os.makedirs(conf_dir, exist_ok=True)
            os.system(f'sudo chown frr:frr {run_dir}'); os.system(f'sudo chown -R frr:frr {conf_dir}')
            with open(f'{conf_dir}/zebra.conf', 'w') as f: f.write(f'hostname r{i}\n')
            with open(f'{conf_dir}/ospfd.conf', 'w') as f: f.write(f'hostname r{i}\nrouter ospf\n ospf router-id 1.1.1.{i}\n network 0.0.0.0/0 area 0\n')
            r.cmd(f'/usr/lib/frr/zebra -d -f {os.path.abspath(conf_dir)}/zebra.conf -z {os.path.abspath(run_dir)}/zebra.api -i {os.path.abspath(run_dir)}/zebra.pid')
            time.sleep(1)
            r.cmd(f'/usr/lib/frr/ospfd -d -f {os.path.abspath(conf_dir)}/ospfd.conf -z {os.path.abspath(run_dir)}/zebra.api -i {os.path.abspath(run_dir)}/ospfd.pid')

        info("--- Waiting for OSPF to converge and stabilize (120 seconds) ---\n")
        time.sleep(120)
        
        info("\n" + "="*50 + "\n--- STARTING AUTOMATED OSPF BENCHMARK ---\n" + "="*50 + "\n")
        results = []
        hosts = [node for node in net.hosts if 'h' in node.name]
        
        info("--- Starting all iperf servers in background... ---\n")
        for h in hosts: h.cmd('iperf -s &')
        info("--- Waiting 5 seconds for all servers to be ready... ---\n"); time.sleep(5)

        info("--- Running all client tests... ---\n")
        for source in hosts:
            for dest in hosts:
                if source == dest: continue
                dest_id = int(dest.name.replace('h', '')); dest_ip = f'10.0.{dest_id}.10'
                info(f"--- Measuring from {source.name} -> {dest.name} ({dest_ip}) ---\n")
                iperf_output = source.cmd(f'iperf -c {dest_ip} -t 5')
                ping_output = source.cmd(f'ping -c 5 {dest_ip}')
                throughput = parse_iperf(iperf_output); latency, packet_loss = parse_ping(ping_output)
                results.append({'source': source.name, 'destination': dest.name,
                    'throughput_mbps': throughput, 'avg_latency_ms': latency,
                    'packet_loss_percent': packet_loss})
                info(f"Result: Tput={throughput} Mbps, Latency={latency} ms, Loss={packet_loss}%\n")

        info("--- Cleaning up all iperf servers... ---\n")
        for h in hosts: h.cmd('kill %iperf')

        output_path = '../Result/logs/ospf_results.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys()); writer.writeheader(); writer.writerows(results)
        info(f"--- Benchmark complete. Results saved to: {output_path} ---\n")

    finally:
        info("--- Cleaning up and stopping Mininet ---\n")
        net.stop()
        cleanup_frr()

if __name__ == '__main__':
    setLogLevel('info')
    run_ospf_simulation()