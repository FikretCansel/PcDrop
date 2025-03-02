import tkinter as tk
from tkinter import filedialog, ttk
import os
import asyncio
import websockets
import threading
import time
# Import directly from config instead of through __init__
from src.config import config, save_config, upload_directory, shared_directory
from src.utils import base_path, LOCAL_IP

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
    
    # Set window size and make it non-resizable
    window_width = 800
    window_height = 700  # Increased height for message area
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.resizable(False, False)

    # Configure style
    style = ttk.Style()
    style.configure('TButton', padding=10, font=('Segoe UI', 11))
    style.configure('TLabel', font=('Segoe UI', 11))
    style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'))
    style.configure('Status.TLabel', font=('Segoe UI', 12), foreground='green')
    style.configure('Address.TLabel', font=('Segoe UI', 11), foreground='blue')

    # Main frame with padding
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    title_label = ttk.Label(header_frame, text="PcDrop", style='Header.TLabel')
    title_label.pack()

    # Content frame with two columns
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left column for incoming files
    left_frame = ttk.LabelFrame(content_frame, text="Gelen Dosyaların Klasörü", padding="10")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    def update_label(label, text):
        label.config(text=text)

    def change_upload_directory():
        global upload_directory
        new_directory = select_directory("Yükleme Klasörünü Seç", upload_directory)
        if new_directory:
            upload_directory = new_directory
            config["upload_directory"] = upload_directory
            save_config(config)
            update_label(upload_path_label, upload_directory)

    def change_shared_directory():
        global shared_directory
        new_directory = select_directory("Paylaşılan Klasörü Seç", shared_directory)
        if new_directory:
            shared_directory = new_directory
            config["shared_directory"] = shared_directory
            save_config(config)
            update_label(shared_path_label, shared_directory)

    def go_to_folder():
        os.startfile(upload_directory)

    def go_to_shared_folder():
        os.startfile(shared_directory)

    # Upload directory controls
    upload_path_label = ttk.Label(left_frame, text=upload_directory, wraplength=300)
    upload_path_label.pack(fill=tk.X, pady=(0, 10))

    # Organize by date checkbox
    organize_var = tk.BooleanVar(value=config.get("organize_by_date", False))
    skip_duplicates_var = tk.BooleanVar(value=config.get("skip_duplicates", False))
    
    def on_checkbox_change():
        config["organize_by_date"] = organize_var.get()
        config["skip_duplicates"] = skip_duplicates_var.get()
        save_config(config)
    
    organize_frame = ttk.Frame(left_frame)
    organize_frame.pack(fill=tk.X, pady=5)
    
    organize_check = ttk.Checkbutton(
        organize_frame, 
        text="Klasörlendirerek taşı (Yıl/Ay bazında)", 
        variable=organize_var,
        command=on_checkbox_change
    )
    organize_check.pack(side=tk.LEFT)
    
    # Skip duplicates checkbox
    skip_duplicates_check = ttk.Checkbutton(
        organize_frame,
        text="Aynı isimdeki dosyaları atla",
        variable=skip_duplicates_var,
        command=on_checkbox_change
    )
    skip_duplicates_check.pack(side=tk.LEFT, padx=(10, 0))

    upload_buttons_frame = ttk.Frame(left_frame)
    upload_buttons_frame.pack(fill=tk.X, pady=5)

    change_upload_btn = ttk.Button(upload_buttons_frame, text="Klasör Değiştir", command=change_upload_directory)
    change_upload_btn.pack(side=tk.LEFT, padx=(0, 5))

    goto_upload_btn = ttk.Button(upload_buttons_frame, text="Klasöre Git", command=go_to_folder)
    goto_upload_btn.pack(side=tk.LEFT)

    # Right column for shared files
    right_frame = ttk.LabelFrame(content_frame, text="Paylaşılan(Giden) Dosyaların Klasörü", padding="10")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    shared_path_label = ttk.Label(right_frame, text=shared_directory, wraplength=300)
    shared_path_label.pack(fill=tk.X, pady=(0, 10))

    shared_buttons_frame = ttk.Frame(right_frame)
    shared_buttons_frame.pack(fill=tk.X, pady=5)

    change_shared_btn = ttk.Button(shared_buttons_frame, text="Klasör Değiştir", command=change_shared_directory)
    change_shared_btn.pack(side=tk.LEFT, padx=(0, 5))

    goto_shared_btn = ttk.Button(shared_buttons_frame, text="Klasöre Git", command=go_to_shared_folder)
    goto_shared_btn.pack(side=tk.LEFT)

    # Message section with improved WebSocket handling
    message_frame = ttk.LabelFrame(main_frame, text="Mesajlaşma", padding="10")
    message_frame.pack(fill=tk.X, pady=10)

    message_text = tk.Text(message_frame, height=3, width=50)
    message_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    websocket_connection = None
    connection_retry_count = 0

    def send_message():
        message = message_text.get("1.0", tk.END).strip()
        if message:
            asyncio.run(send_ws_message(message))
            message_text.delete("1.0", tk.END)

    send_button = ttk.Button(message_frame, text="Gönder", command=send_message)
    send_button.pack(side=tk.RIGHT)

    received_text = tk.Text(message_frame, height=3, width=50, state='disabled')
    received_text.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=(10, 0))

    async def connect_websocket():
        global websocket_connection, connection_retry_count
        uri = f"ws://{LOCAL_IP}:8000/ws"
        
        while True:
            try:
                if websocket_connection is None:
                    websocket_connection = await websockets.connect(uri)
                    connection_retry_count = 0
                    root.after(0, update_connection_status, True)
                
                message = await websocket_connection.recv()
                root.after(0, update_received_text, message)
            except websockets.ConnectionClosed:
                websocket_connection = None
                root.after(0, update_connection_status, False)
                await asyncio.sleep(min(2 ** connection_retry_count, 30))
                connection_retry_count += 1
            except Exception as e:
                print(f"WebSocket error: {e}")
                websocket_connection = None
                root.after(0, update_connection_status, False)
                await asyncio.sleep(5)

    def update_received_text(message):
        received_text.config(state='normal')
        received_text.delete("1.0", tk.END)
        received_text.insert("1.0", message)
        received_text.config(state='disabled')

    def update_connection_status(is_connected):
        if is_connected:
            server_status.config(text="✓ Sunucu Çalışıyor (Mesajlaşma Bağlı)")
        else:
            server_status.config(text="⚠ Sunucu Çalışıyor (Mesajlaşma Bağlantısı Kesik)")

    async def send_ws_message(message):
        global websocket_connection
        if websocket_connection:
            try:
                await websocket_connection.send(message)
            except:
                websocket_connection = None
                root.after(0, update_connection_status, False)

    def start_websocket():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(connect_websocket())

    # Start WebSocket connection in a separate thread
    threading.Thread(target=start_websocket, daemon=True).start()

    # Status section at bottom with initial connection status
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(20, 0))

    server_status = ttk.Label(status_frame, text="✓ Sunucu Çalışıyor (Mesajlaşma Bağlanıyor...)", style='Status.TLabel')
    server_status.pack()

    address_label = ttk.Label(status_frame, text=f"http://{LOCAL_IP}:8000", style='Address.TLabel')
    address_label.pack(pady=5)

    # Info text
    info_label = ttk.Label(status_frame, text="Web tarayıcınızdan yukarıdaki adrese giderek\ndosyalarınızı yönetebilirsiniz", 
                          justify=tk.CENTER)
    info_label.pack(pady=10)

    def on_closing():
        print("Application is shutting down...")
        root.destroy()
        os._exit(0)

    # Set window icon
    root.iconbitmap(os.path.join(base_path, "static", "favicon.ico"))
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()