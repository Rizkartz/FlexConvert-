import os
import uuid
import asyncio
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil

from app.utils import SUPPORTED_FORMATS, create_temp_dir, cleanup_temp_files, check_ffmpeg, get_file_extension
from app.converters import convert_file

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="FlexConvert API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_temp_dir()

def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

@app.post("/api/convert")
async def api_convert(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: str = Form(...)
):
    try:
        # Check size (100MB max approximation as reading full file into memory)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")

        ext = get_file_extension(file.filename)
        output_format = output_format.lower().replace('.', '')
        
        # Save uploaded file
        unique_id = uuid.uuid4().hex
        safe_filename = f"{unique_id}_{file.filename}"
        input_path = os.path.join('temp', 'uploads', safe_filename)
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Convert
        output_dir = os.path.join('temp', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            output_path = convert_file(input_path, output_format, output_dir)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        output_filename = os.path.basename(output_path)
        output_size = os.path.getsize(output_path)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_files, 'temp', 1)
        
        return {
            "success": True,
            "filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "original_name": file.filename,
            "original_format": ext,
            "output_format": output_format,
            "file_size": output_size,
            "file_size_formatted": format_size(output_size)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join('temp', 'output', filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/api/formats")
async def get_formats():
    return JSONResponse(content=SUPPORTED_FORMATS)

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "ffmpeg_available": check_ffmpeg()
    }

@app.get("/")
async def root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return HTMLResponse(content="<h1>FlexConvert - Frontend not found</h1><p>Place index.html in static/ directory.</p>")

# Mount static files AFTER all routes to avoid route conflicts
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

