import sys
import os
from pathlib import Path
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
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
app.mount("/shared", StaticFiles(directory=static_folder), name="shared")

templates = Jinja2Templates(directory=templates_folder)

# Ensure the uploads folder and config file exist
DOCUMENTS_PATH = str(Path(os.path.expanduser("~")) / "Documents")
CONFIG_FOLDER = os.path.join(DOCUMENTS_PATH, "PcDrop")
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")

# Create the necessary directories if they don't exist
os.makedirs(CONFIG_FOLDER, exist_ok=True)

# Get local IP address
def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "IP alınamadı"

LOCAL_IP = get_local_ip()

# Load saved directory from config file or use default
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}



def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

config = load_config()
upload_directory = config.get("upload_directory", str(Path(os.path.expanduser("~")) / "Pictures"))
shared_directory = config.get("shared_directory", str(Path(os.path.expanduser("~")) / "Documents"))

def select_directory(title, default_directory):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title, initialdir=default_directory)
    root.destroy()
    return directory

# Start the Tkinter GUI
def start_gui():
    global upload_directory, shared_directory, root

    root = tk.Tk()
    root.title("PcDrop")

    def update_label(label, text):
        label.config(text=text)

    # Set window size and background color
    root.geometry("650x450")
    root.configure(bg="#f0f0f0")

    # Set window icon
    root.iconbitmap(os.path.join(base_path, "static", "favicon.ico"))  # Set the app icon

    # Title label for the window
    title_label = tk.Label(root, text="PcDrop Uygulaması", font=("Arial", 18), bg="#f0f0f0")
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    def change_upload_directory():
        global upload_directory
        new_directory = select_directory("Yükleme Klasörünü Seç", upload_directory)
        if new_directory:
            upload_directory = new_directory
            config["upload_directory"] = upload_directory
            save_config(config)
            update_label(upload_label, f"Yükleme Klasörü: {upload_directory}")

    def change_shared_directory():
        global shared_directory
        new_directory = select_directory("Paylaşılan Klasörü Seç", shared_directory)
        if new_directory:
            shared_directory = new_directory
            config["shared_directory"] = shared_directory
            save_config(config)
            update_label(shared_label, f"Paylaşılan Klasör: {shared_directory}")

    upload_label = tk.Label(root, text=f"Yükleme Klasörü: {upload_directory}", font=("Arial", 12), bg="#f0f0f0")
    upload_label.grid(row=1, column=0, columnspan=2, pady=5)

    upload_button = tk.Button(root, text="Klasör Değiştir", font=("Arial", 12), command=change_upload_directory,
                              bg="#4CAF50", fg="white", relief="raised", width=20)
    upload_button.grid(row=2, column=0, padx=10, pady=20)

    def go_to_folder():
        os.startfile(upload_directory)
    def go_to_shared_folder():
        os.startfile(shared_directory)

    go_to_button = tk.Button(root, text="Klasöre Git", font=("Arial", 12), command=go_to_folder, bg="#2196F3", fg="white", relief="raised", width=20)
    go_to_button.grid(row=2, column=1, padx=10, pady=20)


    shared_label = tk.Label(root, text=f"Paylaşılan Klasör: {shared_directory}", font=("Arial", 12), bg="#f0f0f0")
    shared_label.grid(row=3, column=0, columnspan=2, pady=5)

    shared_button = tk.Button(root, text="Paylaşılan Klasör Değiştir", font=("Arial", 12), command=change_shared_directory,
                              bg="#4CAF50", fg="white", relief="raised", width=20)
    shared_button.grid(row=4, column=0, padx=10, pady=20)

    go_to_button = tk.Button(root, text="Paylaşılan Klasöre Git", font=("Arial", 12), command=go_to_shared_folder, bg="#2196F3",
                             fg="white", relief="raised", width=20)
    go_to_button.grid(row=4, column=1, padx=10, pady=20)


    # Display server status message
    server_status_label = tk.Label(root, text="Çalışıyor...", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="green")
    server_status_label.grid(row=5, column=0, columnspan=2, pady=10)

    # Message about uploading files
    upload_message_label = tk.Label(root, text="Bu adrese giderek dosyalarınızı yükleyebilirsiniz", font=("Arial", 12), bg="#f0f0f0")
    upload_message_label.grid(row=6, column=0, columnspan=2, pady=10)

    # Display the local IP address
    address_label = tk.Label(root, text=f"http://{LOCAL_IP}:8000", font=("Arial", 12), bg="#f0f0f0", fg="blue")
    address_label.grid(row=7, column=0, columnspan=2, pady=20)

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

@app.get("/shared_files", response_class=HTMLResponse)
async def shared_files(request: Request):
    files = os.listdir(shared_directory) if os.path.exists(shared_directory) else []
    return templates.TemplateResponse("shared_files.html", {"request": request, "files": files})

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(shared_directory, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Dosya bulunamadı"}

@app.get("/download_all")
async def download_all(request: Request):
    files = os.listdir(shared_directory)
    file_urls = [f"/download/{file}" for file in files]
    return templates.TemplateResponse("download_all.html", {"request": request, "file_urls": file_urls})

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
