import argparse
import json

import numpy as np
from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.processing.align_images import align_images
from libs.processing.store_results import store_results
from manual_align import process as manual_align_process


class ExportEntry:
    def __init__(self, varname, content, coordinates):
        self.varname = varname if varname else 'Unknown'
        self.content = content if content else ''
        self.coordinates = coordinates if coordinates else {}
        
        self.x = self.coordinates.get('x', 0)
        self.y = self.coordinates.get('y', 0)
        self.width = self.coordinates.get('width', 0)
        self.height = self.coordinates.get('height', 0)


class ExportConfig:
    def __init__(self, width, height, entries):
        self.width = width
        self.height = height
        self.entries = entries

    @classmethod
    def load_from_json(cls, config_file):
        with open(config_file, 'r') as f:
            payload = json.load(f)
        
        entries = []
        for item in payload.get('data', []):
            entries.append(ExportEntry(
                item.get('varname'), 
                item.get('content'), 
                item.get('coordinates')
            ))
            
        return cls(
            payload.get('width'),
            payload.get('height'),
            entries
        )


def main(pdf_logsheet, pdf_template, config_file, output_file, aligned=False, alignment_config=None):
    config = ExportConfig.load_from_json(config_file)

    template_image = convert_pdf_to_image(pdf_template)
    template_image = np.array(template_image)

    logsheet_image = convert_pdf_to_image(pdf_logsheet)
    logsheet_image = np.array(logsheet_image)
    
    if config.width and config.height:
        target_size = (config.width, config.height)
        template_image = resize_image(template_image, target_size)
        logsheet_image = resize_image(logsheet_image, target_size)
    else:
        pass
    
    if alignment_config is not None and not aligned:
        with open(alignment_config, 'r') as f:
            align_config = json.load(f)

        template_points = align_config['template_points']
        target_points = align_config['target_points']
    
        aligned_logsheet = manual_align_process(logsheet_image, template_image, 
                                                template_points=template_points, 
                                                target_points=target_points)
    else:
        print("Warning: Missing alignment points, falling back to automatic alignment.")
        aligned_logsheet = align_images(logsheet_image, template_image, filter_grayscale=False)
    
    if aligned_logsheet is None:
        print("Warning: Alignment failed. Using original image.")
        aligned_logsheet = logsheet_image

    results = []
    
    img_h, img_w, _ = aligned_logsheet.shape

    for entry in config.entries:
        y_start = max(0, entry.y)
        y_end = min(img_h, entry.y + entry.height)
        x_start = max(0, entry.x)
        x_end = min(img_w, entry.x + entry.width)
        
        if entry.width > 0 and entry.height > 0:
            cropped = aligned_logsheet[y_start:y_end, x_start:x_end]
        else:
            cropped = np.zeros((10, 10, 3), dtype=np.uint8)

        results.append([entry.varname, {'inferred': entry.content}, cropped])

    store_results(results, {}, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export logsheet to Excel')
    parser.add_argument('--pdf_logsheet', required=True, help='Path to logsheet PDF')
    parser.add_argument('--pdf_template', required=True, help='Path to template PDF')
    parser.add_argument('--config_file', required=True, help='Path to JSON payload (data + dims)')
    parser.add_argument('--output_file', required=True, help='Path to output XLSX')

    parser.add_argument('--aligned', action=argparse.BooleanOptionalAction, default=False, help='The scanned image is already aligned with template, skip automatic alignment step.')
    parser.add_argument('--alignment_config', type=str, required=False, help='Path to JSON file containing alignment config.')
    
    args = parser.parse_args()
    
    main(args.pdf_logsheet, args.pdf_template, args.config_file, args.output_file, aligned=args.aligned, alignment_config=args.alignment_config)