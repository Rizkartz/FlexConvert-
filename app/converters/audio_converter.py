import os
import subprocess
from app.utils import check_ffmpeg

def convert_audio(input_path: str, output_format: str, output_dir: str) -> str:
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg is not installed or not in PATH")
        
    filename = os.path.basename(input_path)
    base_name, _ = os.path.splitext(filename)
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    codec_map = {
        'mp3': 'libmp3lame',
        'ogg': 'libvorbis',
        'aac': 'aac',
        'flac': 'flac',
        'wav': 'pcm_s16le'
    }
    
    codec = codec_map.get(output_format.lower(), 'copy')
    
    cmd = [
        'ffmpeg',
        '-y', # Overwrite output files without asking
        '-i', input_path,
        '-c:a', codec,
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg audio conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")
        
    return output_path
