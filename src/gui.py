import tkinter as tk
from tkinter import filedialog, ttk
import os
import asyncio
import websockets
import threading
import time
import qrcode
from PIL import Image, ImageTk
from io import BytesIO
from src.config import config, save_config, upload_directory, shared_directory
from src.utils import base_path, LOCAL_IP

def select_directory(title, default_directory):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title, initialdir=default_directory)
    root.destroy()
    return directory

def start_gui():
    root = tk.Tk()
    root.title("PcDrop - Dosya Paylaşım Aracı")

    # Helper functions - Move these to the top before using them in UI elements
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

    websocket_connection = None
    connection_retry_count = 0

    def send_message():
        message = message_text.get("1.0", tk.END).strip()
        if message:
            asyncio.run(send_ws_message(message))
            message_text.delete("1.0", tk.END)

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

    def on_checkbox_change():
        config["organize_by_date"] = organize_var.get()
        config["skip_duplicates"] = skip_duplicates_var.get()
        save_config(config)

    # Window configuration
    window_width = 1200
    window_height = 1000
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.resizable(False, False)

    # Configure styles
    style = ttk.Style()
    style.configure('TButton', padding=10, font=('Segoe UI', 11))
    style.configure('TLabel', font=('Segoe UI', 11))
    style.configure('Header.TLabel', font=('Segoe UI', 26, 'bold'))
    style.configure('Subheader.TLabel', font=('Segoe UI', 14, 'bold'))
    style.configure('Status.TLabel', font=('Segoe UI', 12), foreground='green')
    style.configure('Address.TLabel', font=('Segoe UI', 12), foreground='blue')
    style.configure('Section.TLabelframe.Label', font=('Segoe UI', 12, 'bold'))
    style.configure('Path.TLabel', font=('Segoe UI', 10), foreground='#666666')

    # Main frame with padding
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header with app name and description
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    title_label = ttk.Label(header_frame, text="PcDrop", style='Header.TLabel')
    title_label.pack()
    
    subtitle_label = ttk.Label(header_frame, text="Kolay Dosya Paylaşım Aracı", style='Subheader.TLabel')
    subtitle_label.pack(pady=(5, 0))

    # Add separator after header
    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 20))

    # Content frame with two columns
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left column for upload section
    left_frame = ttk.LabelFrame(content_frame, text="📥 GELEN KUTUSU", padding="15", style='Section.TLabelframe')
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    # Add description label
    ttk.Label(left_frame, 
              text="Bu klasöre diğer cihazlardan yüklenen dosyalar gelir",
              wraplength=350).pack(fill=tk.X, pady=(0, 10))

    # Upload directory controls
    path_frame = ttk.Frame(left_frame)
    path_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(path_frame, text="Klasör Konumu:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
    upload_path_label = ttk.Label(path_frame, text=upload_directory, style='Path.TLabel', wraplength=350)
    upload_path_label.pack(fill=tk.X, pady=(5, 0))

    # Organization options frame
    options_frame = ttk.LabelFrame(left_frame, text="Dosya Organizasyon Seçenekleri", padding=10)
    options_frame.pack(fill=tk.X, pady=(10, 15))
    
    organize_var = tk.BooleanVar(value=config.get("organize_by_date", False))
    skip_duplicates_var = tk.BooleanVar(value=config.get("skip_duplicates", False))
    
    organize_check = ttk.Checkbutton(
        options_frame, 
        text="📁 Yıl/Ay klasörlerine otomatik düzenle", 
        variable=organize_var,
        command=on_checkbox_change
    )
    organize_check.pack(anchor=tk.W, pady=(0, 5))
    
    skip_duplicates_check = ttk.Checkbutton(
        options_frame,
        text="🔄 Aynı isimli dosyaları atla",
        variable=skip_duplicates_var,
        command=on_checkbox_change
    )
    skip_duplicates_check.pack(anchor=tk.W)

    # Buttons frame
    buttons_frame = ttk.Frame(left_frame)
    buttons_frame.pack(fill=tk.X, pady=5)

    change_upload_btn = ttk.Button(buttons_frame, text="📂 Klasör Seç", command=change_upload_directory)
    change_upload_btn.pack(side=tk.LEFT, padx=(0, 5))

    goto_upload_btn = ttk.Button(buttons_frame, text="🔍 Klasörü Aç", command=go_to_folder)
    goto_upload_btn.pack(side=tk.LEFT)

    # Right column for shared files
    right_frame = ttk.LabelFrame(content_frame, text="📤 PAYLAŞIM KUTUSU", padding="15", style='Section.TLabelframe')
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Add description label
    ttk.Label(right_frame, 
              text="Bu klasördeki dosyalar diğer cihazlarla paylaşılır",
              wraplength=350).pack(fill=tk.X, pady=(0, 10))

    # Shared directory path
    shared_path_frame = ttk.Frame(right_frame)
    shared_path_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(shared_path_frame, text="Klasör Konumu:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
    shared_path_label = ttk.Label(shared_path_frame, text=shared_directory, style='Path.TLabel', wraplength=350)
    shared_path_label.pack(fill=tk.X, pady=(5, 0))

    # Shared directory buttons
    shared_buttons_frame = ttk.Frame(right_frame)
    shared_buttons_frame.pack(fill=tk.X, pady=5)

    change_shared_btn = ttk.Button(shared_buttons_frame, text="📂 Klasör Seç", command=change_shared_directory)
    change_shared_btn.pack(side=tk.LEFT, padx=(0, 5))

    goto_shared_btn = ttk.Button(shared_buttons_frame, text="🔍 Klasörü Aç", command=go_to_shared_folder)
    goto_shared_btn.pack(side=tk.LEFT)

    # Add separator before messaging section
    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)

    # Messaging section with improved layout
    message_frame = ttk.LabelFrame(main_frame, text="💬 MESAJLAŞMA", padding="15", style='Section.TLabelframe')
    message_frame.pack(fill=tk.X)

    # Message display area
    received_text = tk.Text(message_frame, height=3, width=50, state='disabled')
    received_text.pack(fill=tk.X, expand=True, pady=(0, 10))

    # Message input area
    input_frame = ttk.Frame(message_frame)
    input_frame.pack(fill=tk.X)

    message_text = tk.Text(input_frame, height=2, width=50)
    message_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    send_button = ttk.Button(input_frame, text="📨 Gönder", command=send_message)
    send_button.pack(side=tk.RIGHT)

    # Status section at bottom
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(20, 0))

    server_status = ttk.Label(status_frame, text="✓ Sunucu Çalışıyor (Mesajlaşma Bağlanıyor...)", style='Status.TLabel')
    server_status.pack()

    # Connection info with improved visibility
    connection_frame = ttk.LabelFrame(status_frame, text="📱 Bağlantı Bilgileri", padding=15)
    connection_frame.pack(pady=10, fill=tk.X)

    # Create QR code
    url = f"http://{LOCAL_IP}:8000"
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="#4361ee", back_color="white")
    
    # Convert QR code to PhotoImage
    qr_bytes = BytesIO()
    qr_image.save(qr_bytes, format='PNG')
    qr_bytes.seek(0)
    qr_photo = ImageTk.PhotoImage(Image.open(qr_bytes))

    # QR code and connection info side by side
    info_container = ttk.Frame(connection_frame)
    info_container.pack(fill=tk.X)

    # Left side - Connection text
    text_frame = ttk.Frame(info_container)
    text_frame.pack(side=tk.LEFT, padx=(0, 20))

    ttk.Label(text_frame, 
             text="Web tarayıcınızdan aşağıdaki adrese giderek\nveya QR kodu mobil cihazınızla okutarak\ndosyalarınızı yönetebilirsiniz:",
             justify=tk.LEFT).pack(anchor=tk.W)

    url_frame = ttk.Frame(text_frame)
    url_frame.pack(fill=tk.X, pady=(10, 0))
    
    address_label = ttk.Label(url_frame, 
                            text=url,
                            style='Address.TLabel',
                            font=('Segoe UI', 14, 'bold'))
    address_label.pack(side=tk.LEFT)

    def copy_url():
        root.clipboard_clear()
        root.clipboard_append(url)
        copy_btn.config(text="✓ Kopyalandı")
        root.after(2000, lambda: copy_btn.config(text="📋 Kopyala"))

    copy_btn = ttk.Button(url_frame, text="📋 Kopyala", command=copy_url)
    copy_btn.pack(side=tk.LEFT, padx=(10, 0))

    # Right side - QR code
    qr_frame = ttk.Frame(info_container)
    qr_frame.pack(side=tk.RIGHT)
    
    qr_label = ttk.Label(qr_frame, image=qr_photo)
    qr_label.image = qr_photo  # Keep a reference!
    qr_label.pack()

    # Update styles
    style = ttk.Style()
    style.configure('TButton', padding=10, font=('Segoe UI', 11))
    style.configure('TLabel', font=('Segoe UI', 11))
    style.configure('Header.TLabel', font=('Segoe UI', 26, 'bold'))
    style.configure('Subheader.TLabel', font=('Segoe UI', 14, 'bold'))
    style.configure('Status.TLabel', font=('Segoe UI', 12), foreground='green')
    style.configure('Address.TLabel', font=('Segoe UI', 12), foreground='blue')
    style.configure('Section.TLabelframe.Label', font=('Segoe UI', 12, 'bold'))
    style.configure('Path.TLabel', font=('Segoe UI', 10), foreground='#666666')

    # Start WebSocket connection in a separate thread
    threading.Thread(target=start_websocket, daemon=True).start()

    def on_closing():
        print("Application is shutting down...")
        root.destroy()
        os._exit(0)

    # Set window icon and start
    root.iconbitmap(os.path.join(base_path, "static", "favicon.ico"))
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()