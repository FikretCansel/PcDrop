import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Request, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from PIL.ExifTags import TAGS
from src.utils import LOCAL_IP, templates_folder
from src.config import config, upload_directory, shared_directory
import asyncio
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory=templates_folder)

# Store active websocket connections
websocket_connections: List[WebSocket] = []

# Store the current message
current_message = ""

async def broadcast_message(message: str):
    """Broadcast message to all connected clients"""
    global current_message
    current_message = message
    for connection in websocket_connections:
        try:
            await connection.send_text(message)
        except:
            websocket_connections.remove(connection)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        # Send current message to new connection
        if current_message:
            await websocket.send_text(current_message)
        
        # Listen for messages
        while True:
            message = await websocket.receive_text()
            await broadcast_message(message)
    except:
        websocket_connections.remove(websocket)

def get_file_date(file_path):
    try:
        # Try to get date from EXIF data if it's an image file
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            with Image.open(file_path) as img:
                exif = img._getexif()
                if exif:
                    for tag_id in exif:
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            date_str = exif[tag_id]
                            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        
        # Use file creation date if no EXIF data or not an image
        return datetime.fromtimestamp(os.path.getctime(file_path))
    except:
        # Use current date in case of any error
        return datetime.now()

def organize_file(file_path):
    if not config.get("organize_by_date", False):
        return file_path

    date = get_file_date(file_path)
    year_folder = str(date.year)
    month_folder = f"{date.month:02d}"
    
    # Create year and month folders
    year_path = os.path.join(upload_directory, year_folder)
    month_path = os.path.join(year_path, month_folder)
    
    os.makedirs(year_path, exist_ok=True)
    os.makedirs(month_path, exist_ok=True)
    
    # Move file to its new location
    filename = os.path.basename(file_path)
    new_path = os.path.join(month_path, filename)
    
    # If skip_duplicates is enabled and file exists, return None
    if config.get("skip_duplicates", False) and os.path.exists(new_path):
        os.remove(file_path)  # Remove the temporary file
        return None
    
    # Add number suffix if file with same name exists
    counter = 1
    base_name, ext = os.path.splitext(filename)
    while os.path.exists(new_path):
        new_filename = f"{base_name}_{counter}{ext}"
        new_path = os.path.join(month_path, new_filename)
        counter += 1
    
    os.rename(file_path, new_path)
    return new_path

@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "local_ip": LOCAL_IP})

@router.get("/shared_files", response_class=HTMLResponse)
async def shared_files(request: Request):
    current_shared_dir = config.get("shared_directory", shared_directory)
    files = os.listdir(current_shared_dir) if os.path.exists(current_shared_dir) else []
    return templates.TemplateResponse("shared_files.html", {"request": request, "files": files})

@router.get("/download/{filename}")
async def download_file(filename: str):
    current_shared_dir = config.get("shared_directory", shared_directory)
    file_path = os.path.join(current_shared_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Dosya bulunamadı"}

@router.get("/download_all")
async def download_all(request: Request):
    files = os.listdir(shared_directory)
    file_urls = [f"/download/{file}" for file in files]
    return templates.TemplateResponse("download_all.html", {"request": request, "file_urls": file_urls})

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    saved_files = []
    skipped_files = []
    
    if upload_directory:
        for file in files:
            temp_path = os.path.join(upload_directory, file.filename)
            
            # Check for duplicates before saving if skip_duplicates is enabled
            target_path = os.path.join(upload_directory, file.filename)
            if config.get("skip_duplicates", False) and os.path.exists(target_path):
                skipped_files.append(file.filename)
                continue
                
            # First save to temporary location
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            
            # Organize file (if organize_by_date is active)
            final_path = organize_file(temp_path)
            if final_path:  # If file wasn't skipped
                saved_files.append(os.path.basename(final_path))
            else:
                skipped_files.append(file.filename)
    else:
        return {"message": "Dosya seçilmedi"}

    message = "Yükleme tamamlandı!"
    if skipped_files:
        message += f" (Tekrarlanan {len(skipped_files)} dosya atlandı)"
        
    return {
        "message": message,
        "filenames": saved_files,
        "skipped": skipped_files
    }