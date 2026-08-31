import os
from PIL import Image

def convert_image(input_path: str, output_format: str, output_dir: str) -> str:
    filename = os.path.basename(input_path)
    base_name, _ = os.path.splitext(filename)
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    with Image.open(input_path) as img:
        # Convert to RGB if saving to JPEG or if it has an alpha channel but target doesn't support it
        if output_format.lower() in ['jpg', 'jpeg', 'bmp'] and img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
            
        if output_format.lower() == 'ico':
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save(output_path, format='ICO', sizes=icon_sizes)
        elif output_format.lower() == 'gif' and getattr(img, "is_animated", False):
            # Save animated gif
            img.save(output_path, save_all=True)
        else:
            save_kwargs = {}
            if output_format.lower() in ['jpg', 'jpeg', 'webp']:
                save_kwargs['quality'] = 95
            img.save(output_path, format=output_format.upper() if output_format.lower() != 'jpg' else 'JPEG', **save_kwargs)
            
    return output_path
