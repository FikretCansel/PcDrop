import tkinter as tk
from tkinter import filedialog
import os
from .config import config, save_config, upload_directory, shared_directory
from .utils import LOCAL_IP, base_path

def select_directory(title, default_directory):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title, initialdir=default_directory)
    root.destroy()
    return directory

def start_gui():
    global upload_directory, shared_directory

    root = tk.Tk()
    root.title("PcDrop")

    def update_label(label, text):
        label.config(text=text)

    root.geometry("650x450")
    root.configure(bg="#f0f0f0")
    root.iconbitmap(os.path.join(base_path, "static", "favicon.ico"))

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

    def go_to_folder():
        os.startfile(upload_directory)

    def go_to_shared_folder():
        os.startfile(shared_directory)

    upload_label = tk.Label(root, text=f"Yükleme Klasörü: {upload_directory}", font=("Arial", 12), bg="#f0f0f0")
    upload_label.grid(row=1, column=0, columnspan=2, pady=5)

    upload_button = tk.Button(root, text="Klasör Değiştir", font=("Arial", 12), command=change_upload_directory,
                            bg="#4CAF50", fg="white", relief="raised", width=20)
    upload_button.grid(row=2, column=0, padx=10, pady=20)

    go_to_button = tk.Button(root, text="Klasöre Git", font=("Arial", 12), command=go_to_folder,
                            bg="#2196F3", fg="white", relief="raised", width=20)
    go_to_button.grid(row=2, column=1, padx=10, pady=20)

    shared_label = tk.Label(root, text=f"Paylaşılan Klasör: {shared_directory}", font=("Arial", 12), bg="#f0f0f0")
    shared_label.grid(row=3, column=0, columnspan=2, pady=5)

    shared_button = tk.Button(root, text="Paylaşılan Klasör Değiştir", font=("Arial", 12), command=change_shared_directory,
                            bg="#4CAF50", fg="white", relief="raised", width=20)
    shared_button.grid(row=4, column=0, padx=10, pady=20)

    go_to_shared = tk.Button(root, text="Paylaşılan Klasöre Git", font=("Arial", 12), command=go_to_shared_folder,
                            bg="#2196F3", fg="white", relief="raised", width=20)
    go_to_shared.grid(row=4, column=1, padx=10, pady=20)

    server_status_label = tk.Label(root, text="Çalışıyor...", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="green")
    server_status_label.grid(row=5, column=0, columnspan=2, pady=10)

    upload_message_label = tk.Label(root, text="Bu adrese giderek dosyalarınızı yükleyebilirsiniz",
                                  font=("Arial", 12), bg="#f0f0f0")
    upload_message_label.grid(row=6, column=0, columnspan=2, pady=10)

    address_label = tk.Label(root, text=f"http://{LOCAL_IP}:8000", font=("Arial", 12), bg="#f0f0f0", fg="blue")
    address_label.grid(row=7, column=0, columnspan=2, pady=20)

    def on_closing():
        print("Application is shutting down...")
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()