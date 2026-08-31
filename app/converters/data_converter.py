import os
import json
import yaml
import csv
import xml.etree.ElementTree as ET

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    if not isinstance(d, dict):
        return [(parent_key, d)]
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)

def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    if isinstance(d, dict):
        for key, val in d.items():
            child = dict_to_xml(str(key), val)
            elem.append(child)
    elif isinstance(d, list):
        for val in d:
            child = dict_to_xml('item', val)
            elem.append(child)
    else:
        elem.text = str(d)
    return elem

def convert_data(input_path: str, output_format: str, output_dir: str) -> str:
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    ext = ext.lower().replace('.', '')
    output_filename = f"{base_name}.{output_format}"
    output_path = os.path.join(output_dir, output_filename)
    
    data = None
    
    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        if ext == 'json':
            data = json.load(f)
        elif ext in ['yaml', 'yml']:
            data = yaml.safe_load(f)
        elif ext == 'xml':
            # Simplified XML reading to dict (very naive, usually use xmltodict)
            tree = ET.parse(f)
            root = tree.getroot()
            # For simplicity, convert tree to dict recursively
            def xml_to_dict(element):
                if len(element) == 0:
                    return element.text
                return {child.tag: xml_to_dict(child) for child in element}
            data = {root.tag: xml_to_dict(root)}
        elif ext == 'csv':
            reader = csv.DictReader(f)
            data = [row for row in reader]
        else:
            raise ValueError(f"Unsupported data input format: {ext}")
            
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        if output_format == 'json':
            json.dump(data, f, indent=2)
        elif output_format == 'yaml':
            yaml.dump(data, f, default_flow_style=False)
        elif output_format == 'xml':
            root_tag = 'root'
            xml_elem = dict_to_xml(root_tag, data)
            tree = ET.ElementTree(xml_elem)
            tree.write(f, encoding='unicode', xml_declaration=True)
        elif output_format == 'csv':
            if isinstance(data, dict):
                data = [data] # Wrap in list
            if isinstance(data, list) and len(data) > 0:
                # Flatten the dictionaries in the list
                flat_data = [flatten_dict(item) if isinstance(item, dict) else {'value': item} for item in data]
                keys = set()
                for item in flat_data:
                    keys.update(item.keys())
                writer = csv.DictWriter(f, fieldnames=list(keys))
                writer.writeheader()
                writer.writerows(flat_data)
            else:
                f.write("") # empty or unsupported structural conversion
        else:
            raise ValueError(f"Unsupported data output format: {output_format}")
            
    return output_path
