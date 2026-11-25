import os
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request

DEVICE_KEY = os.environ["DEVICE_KEY"]
FRAMES_DIR = Path("/data/frames")
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Face Access API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/frame")
async def receive_frame(request: Request, x_device_key: str = Header(...)):
    if not secrets.compare_digest(x_device_key, DEVICE_KEY):
        raise HTTPException(status_code=401, detail="Invalid device key")

    data = await request.body()
    if not data.startswith(b"\xff\xd8"):  # сигнатура JPEG
        raise HTTPException(status_code=400, detail="Not a JPEG")

    name = f"{int(time.time() * 1000)}.jpg"
    (FRAMES_DIR / name).write_bytes(data)
    return {"status": "ok", "file": name, "size": len(data)}