import os
import zipfile
import tarfile
import py7zr
import shutil
import uuid

def convert_archive(input_path: str, output_format: str, output_dir: str) -> str:
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    if input_path.endswith('.tar.gz'):
        base_name = base_name[:-4]
        ext = '.tar.gz'
    else:
        ext = ext.lower()
        
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    # Create temp extraction dir
    extract_dir = os.path.join(output_dir, f"extract_{uuid.uuid4().hex}")
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        # Extract
        if ext == '.zip':
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif ext in ['.tar', '.tar.gz', '.tgz']:
            with tarfile.open(input_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
        elif ext == '.7z':
            with py7zr.SevenZipFile(input_path, mode='r') as z:
                z.extractall(path=extract_dir)
        else:
            raise ValueError(f"Unsupported archive input format: {ext}")
            
        # Repack
        if output_format == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, extract_dir)
                        zipf.write(file_path, arcname)
        elif output_format == 'tar':
            with tarfile.open(output_path, "w") as tar:
                tar.add(extract_dir, arcname=os.path.basename(extract_dir))
        elif output_format == 'tar.gz':
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(extract_dir, arcname=os.path.basename(extract_dir))
        else:
            raise ValueError(f"Unsupported archive output format: {output_format}")
            
    finally:
        # Cleanup
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            
    return output_path
