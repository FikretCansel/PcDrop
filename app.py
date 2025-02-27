import sys
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import socket
import threading
import tkinter as tk
from tkinter import filedialog

if getattr(sys, 'frozen', False):
    # Eğer PyInstaller ile paketlendiyse
    base_path = sys._MEIPASS
else:
    # Geliştirme aşamasında
    base_path = os.path.abspath(".")

static_folder = os.path.join(base_path, "static")
templates_folder = os.path.join(base_path, "templates")


app = FastAPI()

# Statik dosyalar için klasör ayarlıyoruz
app.mount("/static", StaticFiles(directory=static_folder), name="static")

# Jinja2 şablonları için klasör ayarlıyoruz
templates = Jinja2Templates(directory=templates_folder)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Bilgisayarın yerel (local) IP adresini almak için
def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "IP alınamadı"

LOCAL_IP = get_local_ip()

# Tkinter GUI'yi çalıştıran fonksiyon
def select_directory():
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    directory = filedialog.askdirectory(title="Dosyanın Yükleneceği Klasörü Seçin")
    root.destroy()  # Pencereyi kapat
    return directory

# Tkinter GUI'yi çalıştıran fonksiyon thread üzerinden çalıştırılacak
def start_gui():
    global upload_directory
    upload_directory = select_directory()
    print(f"Seçilen Klasör: {upload_directory}")
    root = tk.Tk()
    root.title("Dosya Yükleme Arayüzü")
    root.mainloop()

# FastAPI uygulamasını başlatırken tkinter GUI'sini thread'de çalıştır
@app.on_event("startup")
async def startup_event():
    print("\n📢 **Uygulama Çalışıyor!**")
    print(f"🌍 **Bağlantı için:** http://{LOCAL_IP}:8000\n")
    # Tkinter GUI'yi başlatmak için ayrı bir thread kullanıyoruz
    threading.Thread(target=start_gui).start()

@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "local_ip": LOCAL_IP})

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    saved_files = []
    if upload_directory:  # Eğer bir klasör seçildiyse
        for file in files:
            file_path = os.path.join(upload_directory, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_files.append(file.filename)
    else:
        return {"message": "Bir klasör seçmediniz!"}

    return {"message": "Dosyalar başarıyla yüklendi!", "filenames": saved_files}

if __name__ == "__main__":
    import uvicorn

    # Uygulama çalışırken Tkinter penceresini başlatacak
    print(f"🌍 **Bağlantı için:** http://{LOCAL_IP}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, log_level="debug")