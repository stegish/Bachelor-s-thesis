from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Dict, Any
import os
import zipfile
import io
from datetime import datetime
from ....infrastructure.config import Container, get_settings, Settings
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/files")
async def list_files(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """List available analytics files"""
    output_dir = settings.output_directory
    files = []
    
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    "name": filename,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    "type": filename.split('.')[-1]
                })
    
    return {
        "files": sorted(files, key=lambda x: x['modified'], reverse=True),
        "total": len(files)
    }

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    settings: Settings = Depends(get_settings)
) -> FileResponse:
    """Download a specific analytics file"""
    # Security: prevent path traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(settings.output_directory, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.get("/download-all")
async def download_all(settings: Settings = Depends(get_settings)) -> StreamingResponse:
    """Download all analytics files as ZIP"""
    output_dir = settings.output_directory
    
    # Create ZIP in memory
    zip_io = io.BytesIO()
    
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if not file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
    
    zip_io.seek(0)
    
    return StreamingResponse(
        zip_io,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )
