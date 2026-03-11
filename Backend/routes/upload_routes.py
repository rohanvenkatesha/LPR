from fastapi import APIRouter, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os
import uuid
import asyncio

from services.video_service import process_video

router = APIRouter()

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

CSV_FILE = os.path.join(TEMP_FOLDER, "plates_log.csv")


# -----------------------------
# WebSocket Managers
# -----------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


# -----------------------------
# Health Check
# -----------------------------
@router.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "License Plate Recognition API is running"
    }


# -----------------------------
# Upload Video
# -----------------------------
@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):

    # Validate format
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        return {"status": "error", "message": "Unsupported video format"}

    # Save uploaded file
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(TEMP_FOLDER, unique_filename)

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        return {"status": "error", "message": f"Failed to save file: {str(e)}"}

    # Cleanup temp file
    def cleanup_temp_file(path):
        if os.path.exists(path):
            os.remove(path)

    # Background processing
    def background_process(path):

        # WebSocket callback for each detected plate
        def websocket_callback(data):
            asyncio.run(manager.broadcast(data))

        # Run video processing
        process_video(path, websocket_callback=websocket_callback)

        # Notify frontend that video processing finished
        asyncio.run(manager.broadcast({"type": "video_complete"}))

        cleanup_temp_file(path)

    if background_tasks:
        background_tasks.add_task(background_process, temp_path)
    else:
        background_process(temp_path)

    return {
        "status": "success",
        "message": "Video uploaded successfully. Plates will stream live."
    }


# -----------------------------
# WebSocket Endpoint
# -----------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()  # keep connection alive

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket disconnected")


# -----------------------------
# Download CSV
# -----------------------------
@router.get("/download-csv")
def download_csv():

    if not os.path.exists(CSV_FILE):
        return {
            "status": "error",
            "message": "CSV file not ready yet"
        }

    return FileResponse(
        path=CSV_FILE,
        filename="plates_log.csv",
        media_type="text/csv"
    )

# 2. Endpoint to force a download of the video file
@router.get("/download-video")
def download_video():
    video_path = "temp/detected_output.mp4" # Adjust path to your processed video
    if not os.path.exists(video_path):
        return {"status": "error", "message": "Video not found"}
    
    return FileResponse(
        path=video_path,
        filename="processed_analysis.mp4",
        media_type="video/mp4"
    )