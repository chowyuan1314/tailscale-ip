import requests
import yaml
import os

def fetch_derp_ips():
    url = "https://controlplane.tailscale.com/derpmap/default"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        ipv4_set = set()
        ipv6_set = set()

        # 遍历所有区域和节点
        for region in data.get("Regions", {}).values():
            for node in region.get("Nodes", []):
                ipv4 = node.get("IPv4")
                ipv6 = node.get("IPv6")
                
                if ipv4:
                    # 某些字段可能包含端口，只取 IP 部分
                    ip = ipv4.split(':')[0]
                    ipv4_set.add(f"IP-CIDR,{ip}/32")
                if ipv6:
                    ip = ipv6.split(']')[0].replace('[', '') # 处理可能的 IPv6 格式
                    ipv6_set.add(f"IP-CIDR6,{ip}/128")

        # 合并并排序，保持文件整洁
        all_rules = sorted(list(ipv4_set)) + sorted(list(ipv6_set))
        return all_rules
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def save_to_yaml(rules, filename="tailscale_derp.yaml"):
    payload = {
        "payload": rules
    }
    with open(filename, "w", encoding="utf-8") as f:
        # 使用 yaml.dump 生成符合 Mihomo 格式的文件
        # 不使用默认的引用符号，保持简洁
        f.write("payload:\n")
        for rule in rules:
            f.write(f"  - {rule}\n")

if __name__ == "__main__":
    rules = fetch_derp_ips()
    if rules:
        save_to_yaml(rules)
        print(f"成功更新 {len(rules)} 条规则")
    else:
        print("未发现有效规则，跳过更新")
