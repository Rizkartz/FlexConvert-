import os
import pandas as pd
import json

def convert_spreadsheet(input_path: str, output_format: str, output_dir: str) -> str:
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    ext = ext.lower().replace('.', '')
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    # Read input
    if ext == 'xlsx':
        df = pd.read_excel(input_path, engine='openpyxl')
    elif ext == 'csv':
        df = pd.read_csv(input_path)
    elif ext == 'tsv':
        df = pd.read_csv(input_path, sep='\t')
    elif ext == 'json':
        df = pd.read_json(input_path)
    else:
        raise ValueError(f"Unsupported spreadsheet input format: {ext}")
        
    # Write output
    if output_format == 'xlsx':
        df.to_excel(output_path, index=False, engine='openpyxl')
    elif output_format == 'csv':
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    elif output_format == 'tsv':
        df.to_csv(output_path, index=False, sep='\t', encoding='utf-8-sig')
    elif output_format == 'json':
        df.to_json(output_path, orient='records', force_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported spreadsheet output format: {output_format}")
        
    return output_path
