import uvicorn
import sys
import os
import threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils import static_folder, LOCAL_IP
from src.routes import router
from src.gui import start_gui

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_folder), name="static")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("\n📢 **Application is running!**")
    print(f"🌍 **Access it at:** http://{LOCAL_IP}:8000\n")
    threading.Thread(target=start_gui, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)