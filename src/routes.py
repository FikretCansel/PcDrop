import os
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from .utils import LOCAL_IP, templates_folder
from .config import upload_directory, shared_directory

router = APIRouter()
templates = Jinja2Templates(directory=templates_folder)

@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "local_ip": LOCAL_IP})

@router.get("/shared_files", response_class=HTMLResponse)
async def shared_files(request: Request):
    files = os.listdir(shared_directory) if os.path.exists(shared_directory) else []
    return templates.TemplateResponse("shared_files.html", {"request": request, "files": files})

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(shared_directory, filename)
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
    if upload_directory:
        for file in files:
            file_path = os.path.join(upload_directory, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_files.append(file.filename)
    else:
        return {"message": "Bir klasör seçmediniz!"}

    return {"message": "Dosyalar başarıyla yüklendi!", "filenames": saved_files}