
import argparse
import json
import sys

import numpy as np
from libs.pdf_to_image import convert_pdf_to_image


def main(pdf_file, dpi):
    image = convert_pdf_to_image(pdf_file, dpi=dpi)
    image = np.array(image)

    sys.stdout.write(json.dumps({"height": image.shape[0], "width": image.shape[1]}))


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description='Get PDF dimensions as image shape.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_file', type=str, required=True, help='Path to the target PDF file')
    optional.add_argument('--dpi', type=int, required=False, help='DPI for image conversion', default=300)

    args = args_parser.parse_args()
    main(args.pdf_file, args.dpi)
