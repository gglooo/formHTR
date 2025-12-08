import argparse
import io
import json
import sys

import numpy as np
from libs.logsheet_config import LogsheetConfig
from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.processing.align_images import (compute_closest_point,
                                          get_alignment_data, transform)


def preprocess_input(scanned_logsheet, template, page, dpi=300):
    template_image = convert_pdf_to_image(template, dpi=dpi)
    template_image = np.array(template_image)

    logsheet_image = convert_pdf_to_image(scanned_logsheet, page, dpi=dpi)
    logsheet_image = np.array(logsheet_image)

    height, width, _ = logsheet_image.shape

    # resize images
    logsheet_image = resize_image(logsheet_image, (width, height))
    template_image = resize_image(template_image, (width, height))

    return logsheet_image, template_image

def automatic_align(scanned_logsheet, template, page=0):
    (logsheet_image, template_image) = preprocess_input(scanned_logsheet, template, page)
    alignment_data = get_alignment_data(logsheet_image, template_image)

    return alignment_data
    

def main(template_path, target_path, backside_template):
    frontside_alignment_data = automatic_align(target_path, template_path)

    if backside_template:
        backside_alignment_data = automatic_align(target_path, backside_template, page=1)

    data = {
        "frontside": frontside_alignment_data,
        "backside": backside_alignment_data if backside_template else None
    }

    sys.stdout.write(json.dumps(data))

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Extract medatada from logsheet.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_logsheet', type=str, required=True, help='Scanned logsheet in PDF format')
    required.add_argument('--pdf_template', type=str, required=True, help='PDF template of the logsheet')

    optional.add_argument('--backside_template', type=str, help='PDF template of the backside')

    args = args_parser.parse_args()

    main(args.pdf_template, args.pdf_logsheet, args.backside_template)
