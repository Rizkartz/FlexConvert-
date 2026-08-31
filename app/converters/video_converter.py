import os
import subprocess
from app.utils import check_ffmpeg

def convert_video(input_path: str, output_format: str, output_dir: str) -> str:
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg is not installed or not in PATH")
        
    filename = os.path.basename(input_path)
    base_name, _ = os.path.splitext(filename)
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    # Video to GIF requires palette generation for good quality
    if output_format.lower() == 'gif':
        palette_path = os.path.join(output_dir, f"{base_name}_palette.png")
        cmd_palette = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', 'fps=10,scale=320:-1:flags=lanczos,palettegen',
            palette_path
        ]
        cmd_gif = [
            'ffmpeg', '-y', '-i', input_path, '-i', palette_path,
            '-lavfi', 'fps=10,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse',
            output_path
        ]
        
        try:
            subprocess.run(cmd_palette, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(cmd_gif, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg video to GIF conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")
        finally:
            if os.path.exists(palette_path):
                os.remove(palette_path)
                
        return output_path
        
    # Other video formats
    codec_map = {
        'mp4': ['-c:v', 'libx264', '-c:a', 'aac'],
        'webm': ['-c:v', 'libvpx-vp9', '-c:a', 'libopus'],
        'mkv': ['-c:v', 'libx264', '-c:a', 'aac'],
        'avi': ['-c:v', 'mpeg4', '-c:a', 'mp3'],
        'mov': ['-c:v', 'libx264', '-c:a', 'aac']
    }
    
    codecs = codec_map.get(output_format.lower(), [])
    
    cmd = ['ffmpeg', '-y', '-i', input_path] + codecs + [output_path]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg video conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")
        
    return output_path
