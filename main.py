from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import os
import socket

app = FastAPI()

# Statik dosyalar için klasör ayarlıyoruz
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 şablonları için klasör ayarlıyoruz
templates = Jinja2Templates(directory="templates")

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


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "local_ip": LOCAL_IP})


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file.filename)

    return {"message": "Dosyalar başarıyla yüklendi!", "filenames": saved_files}


if __name__ == "__main__":
    import uvicorn

    print("\n📢 **Uygulama Çalışıyor!**")
    print(f"🌍 **Bağlantı için:** http://{LOCAL_IP}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
