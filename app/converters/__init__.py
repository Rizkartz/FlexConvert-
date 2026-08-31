import os
from app.utils import detect_file_type
from .image_converter import convert_image
from .document_converter import convert_document
from .spreadsheet_converter import convert_spreadsheet
from .audio_converter import convert_audio
from .video_converter import convert_video
from .archive_converter import convert_archive
from .data_converter import convert_data

def convert_file(input_path: str, output_format: str, output_dir: str) -> str:
    file_type = detect_file_type(input_path)
    
    # Overrides based on exact matching in case type detection overlaps
    if output_format in ['xlsx', 'csv', 'tsv'] and file_type in ['spreadsheet', 'data']:
        file_type = 'spreadsheet'
    elif output_format in ['json', 'yaml', 'xml'] and file_type in ['spreadsheet', 'data']:
        file_type = 'data'

    if file_type == 'image':
        return convert_image(input_path, output_format, output_dir)
    elif file_type == 'document':
        return convert_document(input_path, output_format, output_dir)
    elif file_type == 'spreadsheet':
        return convert_spreadsheet(input_path, output_format, output_dir)
    elif file_type == 'audio':
        return convert_audio(input_path, output_format, output_dir)
    elif file_type == 'video':
        return convert_video(input_path, output_format, output_dir)
    elif file_type == 'archive':
        return convert_archive(input_path, output_format, output_dir)
    elif file_type == 'data':
        return convert_data(input_path, output_format, output_dir)
    else:
        raise ValueError(f"Unsupported file type for conversion: {file_type}")
