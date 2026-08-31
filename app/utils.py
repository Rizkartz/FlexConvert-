import os
import shutil
import time

SUPPORTED_FORMATS = {
    'image': {
        'extensions': ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'tiff', 'ico'],
        'outputs': ['png', 'jpg', 'bmp', 'gif', 'webp', 'tiff', 'ico']
    },
    'document': {
        'extensions': ['docx', 'txt', 'md', 'html', 'pdf'],
        'outputs': ['pdf', 'docx', 'txt', 'html', 'md']
    },
    'spreadsheet': {
        'extensions': ['xlsx', 'csv', 'json', 'tsv'],
        'outputs': ['xlsx', 'csv', 'json', 'tsv']
    },
    'audio': {
        'extensions': ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'],
        'outputs': ['mp3', 'wav', 'ogg', 'flac', 'aac']
    },
    'video': {
        'extensions': ['mp4', 'avi', 'mkv', 'mov', 'webm', 'flv'],
        'outputs': ['mp4', 'avi', 'mkv', 'mov', 'webm', 'gif']
    },
    'archive': {
        'extensions': ['zip', 'tar', 'gz', 'tgz', '7z'],
        'outputs': ['zip', 'tar', 'tar.gz']
    },
    'data': {
        'extensions': ['json', 'yaml', 'yml', 'xml', 'csv', 'tsv'],
        'outputs': ['json', 'yaml', 'xml', 'csv']
    }
}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().replace('.', '')

def detect_file_type(filename: str) -> str:
    ext = get_file_extension(filename)
    if ext == 'yml':
        ext = 'yaml'
    if ext == 'tgz' or ext == 'gz':
        ext = 'tar.gz' # approximate mapping
        
    for category, formats in SUPPORTED_FORMATS.items():
        if ext in formats['extensions']:
            return category
            
    # Some overlap handling e.g. json in spreadsheet vs data
    if ext == 'json' or ext == 'csv' or ext == 'tsv':
        return 'data'
        
    return 'unknown'

def check_ffmpeg() -> bool:
    return shutil.which('ffmpeg') is not None

def create_temp_dir():
    os.makedirs('temp/uploads', exist_ok=True)
    os.makedirs('temp/output', exist_ok=True)

def cleanup_temp_files(directory='temp', max_age_hours=1):
    if not os.path.exists(directory):
        return
    current_time = time.time()
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if current_time - os.path.getmtime(file_path) > max_age_hours * 3600:
                    os.remove(file_path)
            except Exception:
                pass

def get_output_formats(input_extension: str) -> list:
    ext = input_extension.lower().replace('.', '')
    if ext == 'yml':
        ext = 'yaml'
        
    outputs = set()
    for category, formats in SUPPORTED_FORMATS.items():
        if ext in formats['extensions']:
            outputs.update(formats['outputs'])
    return list(outputs)
