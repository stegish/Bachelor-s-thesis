from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
import os
from typing import List, Dict, Any  # Aggiungi Any qui
from datetime import datetime
from ....infrastructure.config import get_settings, Settings

router = APIRouter(prefix="/csv", tags=["csv"])

@router.get("/list")
async def list_csv_files(settings: Settings = Depends(get_settings)) -> Dict[str, List[Dict[str, Any]]]:  # Cambia any in Any
    """List all available CSV files"""
    try:
        csv_files = []
        output_dir = settings.output_directory
        
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(output_dir, filename)
                    csv_files.append({
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        "path": f"/api/v1/csv/download/{filename}"
                    })
        
        return {
            "files": csv_files,
            "count": len(csv_files),
            "directory": output_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_csv_file(
    filename: str,
    settings: Settings = Depends(get_settings)
) -> FileResponse:
    """Download a specific CSV file"""
    # Security: prevent path traversal
    filename = os.path.basename(filename)
    
    # Only allow CSV files
    if not filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files can be downloaded")
    
    filepath = os.path.join(settings.output_directory, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='text/csv'
    )

@router.get("/download-all-json")
async def download_all_csv_as_json(settings: Settings = Depends(get_settings)):
    """Download all CSV files content as JSON for easy consumption"""
    import pandas as pd
    import numpy as np
    import json
    
    try:
        all_data = {}
        output_dir = settings.output_directory
        
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(output_dir, filename)
                    df = pd.read_csv(filepath)
                    
                    # Replace NaN, Infinity, -Infinity with None (which becomes null in JSON)
                    df = df.replace([np.inf, -np.inf], np.nan)
                    
                    # Convert DataFrame to dict and handle NaN values
                    data_dict = df.to_dict('records')
                    
                    # Clean up the data to ensure JSON compatibility
                    cleaned_data = []
                    for record in data_dict:
                        clean_record = {}
                        for key, value in record.items():
                            if pd.isna(value):
                                clean_record[key] = None
                            elif isinstance(value, (np.integer, np.floating)):
                                # Convert numpy types to Python types
                                if np.isnan(value) or np.isinf(value):
                                    clean_record[key] = None
                                else:
                                    clean_record[key] = float(value) if isinstance(value, np.floating) else int(value)
                            else:
                                clean_record[key] = value
                        cleaned_data.append(clean_record)
                    
                    # Remove .csv extension for key
                    key = filename.replace('.csv', '')
                    all_data[key] = {
                        "columns": df.columns.tolist(),
                        "row_count": len(df),
                        "data": cleaned_data
                    }
        
        # Use JSONResponse to ensure proper serialization
        return JSONResponse(content=all_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))