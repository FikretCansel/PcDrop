import sys
import os
from pathlib import Path
import json
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
def load_directory():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("directory", str(Path(os.path.expanduser("~")) / "Pictures"))
    return str(Path(os.path.expanduser("~")) / "Pictures")

# Save the selected directory to config file
def save_directory(directory):
    config = {"directory": directory}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Open a directory selection dialog
def select_directory(default_directory):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Dosyanın Yükleneceği Klasörü Seçin", initialdir=default_directory)
    root.destroy()
    return directory

# Start the Tkinter GUI
def start_gui():
    global upload_directory, root  # Use global to modify upload_directory

    # Load previously saved directory or use default
    upload_directory = load_directory()

    root = tk.Tk()
    root.title("PcDrop")

    # Set window size and background color
    root.geometry("450x350")
    root.configure(bg="#f0f0f0")

    # Title label for the window
    title_label = tk.Label(root, text="PcDrop Uygulaması", font=("Arial", 18), bg="#f0f0f0")
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Label to show the current selected directory
    directory_label = tk.Label(root, text=f"Yükleme Klasörü: {upload_directory}", font=("Arial", 12), bg="#f0f0f0")
    directory_label.grid(row=1, column=0, columnspan=2, pady=10)

    # Directory change button
    def change_directory():
        global upload_directory  # Use global to modify the global variable
        new_directory = select_directory(upload_directory)
        if new_directory:
            upload_directory = new_directory
            save_directory(upload_directory)  # Save the new directory
            directory_label.config(text=f"Yükleme Klasörü: {upload_directory}")  # Update the label text
            print(f"New selected folder: {upload_directory}")

    # "Klasör Değiştir" button
    change_button = tk.Button(root, text="Klasör Değiştir", font=("Arial", 12), command=change_directory, bg="#4CAF50", fg="white", relief="raised", width=20)
    change_button.grid(row=2, column=0, padx=10, pady=20)

    # "Klasöre Git" button to open the directory in the file explorer
    def go_to_folder():
        os.startfile(upload_directory)  # Opens the folder in the file explorer

    go_to_button = tk.Button(root, text="Klasöre Git", font=("Arial", 12), command=go_to_folder, bg="#2196F3", fg="white", relief="raised", width=20)
    go_to_button.grid(row=2, column=1, padx=10, pady=20)

    # Display server status message
    server_status_label = tk.Label(root, text="Çalışıyor...", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="green")
    server_status_label.grid(row=3, column=0, columnspan=2, pady=10)

    # Message about uploading files
    upload_message_label = tk.Label(root, text="Bu adrese giderek dosyalarınızı yükleyebilirsiniz", font=("Arial", 12), bg="#f0f0f0")
    upload_message_label.grid(row=4, column=0, columnspan=2, pady=10)

    # Display the local IP address
    address_label = tk.Label(root, text=f"http://{LOCAL_IP}:8000", font=("Arial", 12), bg="#f0f0f0", fg="blue")
    address_label.grid(row=5, column=0, columnspan=2, pady=20)

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
