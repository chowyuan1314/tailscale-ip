import requests
import json
import os

def fetch_derp_data():
    url = "https://controlplane.tailscale.com/derpmap/default"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cidrs = set()

        for region in data.get("Regions", {}).values():
            for node in region.get("Nodes", []):
                ipv4 = node.get("IPv4")
                ipv6 = node.get("IPv6")
                
                if ipv4:
                    # 提取 IP 并转为 CIDR 格式
                    ip = ipv4.split(':')[0]
                    cidrs.add(f"{ip}/32")
                
                if ipv6:
                    # 提取 IPv6 并转为 CIDR 格式
                    ip = ipv6.split(']')[0].replace('[', '')
                    cidrs.add(f"{ip}/128")

        return sorted(list(cidrs))
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def save_mihomo_yaml(cidrs, filename="tailscale_derp.yaml"):
    """生成 Mihomo (Clash) 格式的 YAML"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for ip in cidrs:
            # 统一使用 IP-CIDR 标签
            f.write(f"  - IP-CIDR,{ip}\n")

def save_singbox_json(cidrs, filename="tailscale_derp.json"):
    """生成 sing-box 格式的 JSON"""
    data = {
        "version": 3,
        "rules": [
            {
                "ip_cidr": cidrs
            }
        ]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    cidrs = fetch_derp_data()
    if cidrs:
        save_mihomo_yaml(cidrs)
        save_singbox_json(cidrs)
        print(f"成功更新！共提取 {len(cidrs)} 条规则。")
        print("- 已生成 tailscale_derp.yaml (Mihomo)")
        print("- 已生成 tailscale_derp.json (sing-box)")
    else:
        print("未发现有效规则，跳过更新")
