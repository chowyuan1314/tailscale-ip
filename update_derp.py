import requests
import os

def fetch_derp_ips():
    url = "https://controlplane.tailscale.com/derpmap/default"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        ipv4_set = set()
        ipv6_set = set()

        for region in data.get("Regions", {}).values():
            for node in region.get("Nodes", []):
                ipv4 = node.get("IPv4")
                ipv6 = node.get("IPv6")
                
                if ipv4:
                    # 提取 IPv4 并统一使用 IP-CIDR
                    ip = ipv4.split(':')[0]
                    ipv4_set.add(f"IP-CIDR,{ip}/32")
                
                if ipv6:
                    # 提取 IPv6，并按照你的要求将 IP-CIDR6 改为 IP-CIDR
                    ip = ipv6.split(']')[0].replace('[', '')
                    ipv6_set.add(f"IP-CIDR,{ip}/128")

        # 合并结果
        return sorted(list(ipv4_set)) + sorted(list(ipv6_set))
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def save_to_yaml(rules, filename="tailscale_derp.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for rule in rules:
            f.write(f"  - {rule}\n")

if __name__ == "__main__":
    rules = fetch_derp_ips()
    if rules:
        save_to_yaml(rules)
        print(f"成功更新 {len(rules)} 条规则（IPv4/IPv6 均使用 IP-CIDR）")
    else:
        print("未发现有效规则")
