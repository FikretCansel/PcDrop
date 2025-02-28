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

# Determine base path depending on execution mode
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller bundled app
else:
    base_path = os.path.abspath(".")  # Development mode

static_folder = os.path.join(base_path, "static")
templates_folder = os.path.join(base_path, "templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_folder), name="static")
templates = Jinja2Templates(directory=templates_folder)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Get local IP address
def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "IP alınamadı"

LOCAL_IP = get_local_ip()

# Open a directory selection dialog
def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Dosyanın Yükleneceği Klasörü Seçin")
    root.destroy()
    return directory

# Start the Tkinter GUI
def start_gui():
    global upload_directory, root

    upload_directory = select_directory()
    print(f"Selected Folder: {upload_directory}")

    root = tk.Tk()
    root.title("PcDrop")

    # Ensure app exits completely when GUI is closed
    def on_closing():
        print("Application is shutting down...")
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

# Run the GUI in a separate thread
@app.on_event("startup")
async def startup_event():
    print("\n📢 **Application is running!**")
    print(f"🌍 **Access it at:** http://{LOCAL_IP}:8000\n")
    threading.Thread(target=start_gui, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "local_ip": LOCAL_IP})

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    saved_files = []
    if upload_directory:
        for file in files:
            file_path = os.path.join(upload_directory, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_files.append(file.filename)
    else:
        return {"message": "Bir klasör seçmediniz!"}  # User-facing message in Turkish

    return {"message": "Dosyalar başarıyla yüklendi!", "filenames": saved_files}

if __name__ == "__main__":
    import uvicorn
    print(f"🌍 **Access it at:** http://{LOCAL_IP}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
