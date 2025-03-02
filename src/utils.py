import socket
import sys
import os

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "IP alınamadı"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # PyInstaller bundled app
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Development mode - go up one directory from src

LOCAL_IP = get_local_ip()
base_path = get_base_path()
static_folder = os.path.join(base_path, "static")
templates_folder = os.path.join(base_path, "templates")