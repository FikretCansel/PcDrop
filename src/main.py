import threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.utils import static_folder, LOCAL_IP
from src.gui import start_gui
from src.routes import router

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_folder), name="static")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("\n📢 **Application is running!**")
    print(f"🌍 **Access it at:** http://{LOCAL_IP}:8000\n")
    threading.Thread(target=start_gui, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    print(f"🌍 **Access it at:** http://{LOCAL_IP}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)