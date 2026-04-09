# ================================================
# PURE PYTHON CYBERSECURITY IDS DATASET GENERATOR
# ZERO DEPENDENCIES - No numpy, no pandas needed!
# Works on ANY Python version (including your Python 3.14)
# ================================================

import random
import csv
from datetime import datetime, timedelta
from collections import defaultdict

# Set seed for reproducibility
random.seed(42)

n_rows = 12000
n_normal = 7500
n_attack = n_rows - n_normal

protocols = ['TCP', 'UDP', 'ICMP']
common_ports = [80, 443, 22, 21, 53, 25, 110, 143, 3306, 8080, 3389]

def random_ip(is_internal=False):
    if is_internal and random.random() < 0.3:
        return f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

start_time = datetime(2026, 4, 6, 8, 0, 0)

# ====================== NORMAL TRAFFIC ======================
normal_data = []
for _ in range(n_normal):
    src_ip = random_ip(is_internal=True)
    dst_ip = random_ip()
    protocol = random.choices(protocols, weights=[0.72, 0.23, 0.05])[0]
    
    if protocol == 'ICMP':
        src_port = dst_port = 0
    else:
        src_port = random.randint(1024, 65535)
        dst_port = random.choice(common_ports) if random.random() < 0.65 else random.randint(1, 65535)
    
    # Approximate normal distribution for packet size (mean 520, std 180)
    packet_size = max(40, min(1500, int(random.gauss(520, 180))))
    connection_rate = round(random.uniform(0.4, 12.0), 2)
    flow_duration = round(random.uniform(0.5, 180.0), 2)
    timestamp = start_time + timedelta(seconds=random.randint(0, 86400))
    
    normal_data.append([
        timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
        packet_size, connection_rate, flow_duration, 0, 'normal'
    ])

# ====================== ATTACK TRAFFIC ======================
attack_data = []

# 1. Port Scanning
scan_src = "192.168.1.100"
for _ in range(600):
    src_ip = scan_src
    dst_ip = random_ip()
    protocol = random.choice(['TCP', 'UDP'])
    src_port = random.randint(1024, 65535)
    dst_port = random.randint(1, 65535)
    packet_size = random.randint(40, 120)
    connection_rate = random.randint(120, 800)
    flow_duration = round(random.uniform(0.1, 5.0), 2)
    timestamp = start_time + timedelta(seconds=random.randint(3600, 7200))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'port_scan'])

# 2. DDoS
ddos_src = "10.0.0.55"
ddos_dst = "172.16.0.10"
for _ in range(800):
    src_ip = ddos_src
    dst_ip = ddos_dst
    protocol = random.choice(['TCP', 'UDP'])
    src_port = random.randint(1024, 65535)
    dst_port = 80 if protocol == 'TCP' else 53
    packet_size = random.randint(80, 600)
    connection_rate = random.randint(1200, 15000)
    flow_duration = round(random.uniform(30, 300), 2)
    timestamp = start_time + timedelta(seconds=random.randint(7200, 14400))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'ddos'])

# 3. Brute Force
brute_src = "45.67.89.123"
for _ in range(700):
    src_ip = brute_src
    dst_ip = random_ip()
    protocol = 'TCP'
    src_port = random.randint(1024, 65535)
    dst_port = random.choice([22, 80, 443, 3389])
    packet_size = random.randint(60, 400)
    connection_rate = random.randint(40, 350)
    flow_duration = round(random.uniform(1, 20), 2)
    timestamp = start_time + timedelta(seconds=random.randint(14400, 21600))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'brute_force'])

# 4. SYN Flood
for _ in range(500):
    src_ip = random_ip()
    dst_ip = random_ip()
    protocol = 'TCP'
    src_port = random.randint(1024, 65535)
    dst_port = random.choice([80, 443])
    packet_size = random.randint(40, 80)
    connection_rate = random.randint(600, 5000)
    flow_duration = round(random.uniform(0.05, 2.0), 2)
    timestamp = start_time + timedelta(seconds=random.randint(21600, 28800))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'syn_flood'])

# 5. UDP/ICMP Flood
for _ in range(600):
    src_ip = random_ip()
    dst_ip = random_ip()
    protocol = random.choice(['UDP', 'ICMP'])
    src_port = 0 if protocol == 'ICMP' else random.randint(1024, 65535)
    dst_port = 0 if protocol == 'ICMP' else random.randint(1, 65535)
    packet_size = random.randint(50, 300)
    connection_rate = random.randint(900, 12000)
    flow_duration = round(random.uniform(10, 120), 2)
    timestamp = start_time + timedelta(seconds=random.randint(28800, 36000))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'udp_icmp_flood'])

# 6. Data Exfiltration
for _ in range(400):
    src_ip = random_ip()
    dst_ip = random_ip()
    protocol = random.choice(['TCP', 'UDP'])
    src_port = random.randint(1024, 65535)
    dst_port = random.randint(40000, 65535)
    packet_size = random.randint(800, 4500)
    connection_rate = round(random.uniform(0.8, 6.0), 2)
    flow_duration = round(random.uniform(60, 600), 2)
    timestamp = start_time + timedelta(seconds=random.randint(36000, 43200))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'exfiltration'])

# 7. Large Packet Anomaly
for _ in range(400):
    src_ip = random_ip()
    dst_ip = random_ip()
    protocol = random.choice(protocols)
    src_port = 0 if protocol == 'ICMP' else random.randint(1024, 65535)
    dst_port = 0 if protocol == 'ICMP' else random.randint(1, 65535)
    packet_size = random.randint(1600, 9000)
    connection_rate = round(random.uniform(2.0, 25.0), 2)
    flow_duration = round(random.uniform(1, 30), 2)
    timestamp = start_time + timedelta(seconds=random.randint(43200, 50400))
    attack_data.append([timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                        packet_size, connection_rate, flow_duration, 1, 'large_packet'])

# ====================== COMBINE & SHUFFLE ======================
all_data = normal_data + attack_data
random.shuffle(all_data)

columns = ['timestamp', 'src_ip', 'dst_ip', 'protocol', 'src_port', 'dst_port',
           'packet_size', 'connection_rate', 'flow_duration', 'label', 'attack_type']

# ====================== FEATURE ENGINEERING (Pure Python) ======================
print("🚀 Applying feature engineering (pure Python)...")

# Convert to list of dicts for easier processing
data_dicts = [dict(zip(columns, row)) for row in all_data]

# 1. Port Entropy & Unique dst ports
src_port_map = defaultdict(list)
for row in data_dicts:
    src_port_map[row['src_ip']].append(row['dst_port'])

for row in data_dicts:
    ports = src_port_map[row['src_ip']]
    row['port_entropy'] = len(set(ports))
    row['unique_dst_ports'] = len(set(ports))

# 2. Packet Size Z-Score (manual calculation)
packet_sizes = [row['packet_size'] for row in data_dicts]
mean_ps = sum(packet_sizes) / len(packet_sizes)
std_ps = (sum((x - mean_ps) ** 2 for x in packet_sizes) / len(packet_sizes)) ** 0.5
for row in data_dicts:
    row['packet_size_zscore'] = round((row['packet_size'] - mean_ps) / std_ps if std_ps != 0 else 0, 4)

# 3. Rate vs Duration Ratio
for row in data_dicts:
    row['rate_vs_duration_ratio'] = round(row['connection_rate'] / (row['flow_duration'] + 0.001), 4)

# 4. Large Packet Flag
for row in data_dicts:
    row['large_packet_flag'] = 1 if row['packet_size'] > 1500 else 0

# 5. Connection Count per Minute
from collections import Counter
time_floor = defaultdict(int)
for row in data_dicts:
    minute = row['timestamp'].replace(second=0, microsecond=0)
    time_floor[minute] += 1

for row in data_dicts:
    minute = row['timestamp'].replace(second=0, microsecond=0)
    row['connection_count_per_min'] = time_floor[minute]

# 6. src_ip_frequency
ip_count = defaultdict(int)
for row in data_dicts:
    ip_count[row['src_ip']] += 1
for row in data_dicts:
    row['src_ip_frequency'] = ip_count[row['src_ip']]

# 7. ICMP Ratio
icmp_count = defaultdict(int)
total_count = defaultdict(int)
for row in data_dicts:
    total_count[row['src_ip']] += 1
    if row['protocol'] == 'ICMP':
        icmp_count[row['src_ip']] += 1
for row in data_dicts:
    row['icmp_ratio'] = round(icmp_count[row['src_ip']] / total_count[row['src_ip']], 4)

# 8. Anomaly Score
for row in data_dicts:
    row['anomaly_score'] = round(
        abs(row['packet_size_zscore']) * 0.4 +
        row['rate_vs_duration_ratio'] / 100 * 0.3 +
        row['large_packet_flag'] * 0.3, 4)

# ====================== SAVE TO CSV ======================
final_columns = columns + ['port_entropy', 'unique_dst_ports', 'packet_size_zscore',
                           'rate_vs_duration_ratio', 'large_packet_flag',
                           'connection_count_per_min', 'src_ip_frequency',
                           'icmp_ratio', 'anomaly_score']

with open('best_engineered_ids_dataset_12000.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=final_columns)
    writer.writeheader()
    for row in data_dicts:
        writer.writerow(row)

# Quick 5000-row test version
sample = random.sample(data_dicts, 5000)
with open('best_engineered_ids_dataset_5000.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=final_columns)
    writer.writeheader()
    for row in sample:
        writer.writerow(row)

print("✅ SUCCESS! Pure Python dataset generated with ZERO dependencies!")
print(f"📊 Full dataset: 12,000 rows → best_engineered_ids_dataset_12000.csv")
print(f"📊 Quick test:   5,000 rows → best_engineered_ids_dataset_5000.csv")
print(f"🛡️ Attack types included: port_scan, ddos, brute_force, syn_flood, udp_icmp_flood, exfiltration, large_packet")
print("\nJust run this script again anytime — no numpy/pandas required!")