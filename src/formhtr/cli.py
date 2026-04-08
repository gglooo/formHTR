from __future__ import annotations

import argparse
import sys

from . import __version__
from .logsheet import load_credentials, process_logsheet_to_xlsx
from .manual_align import manual_align_pdf
from .roi_tools import annotate_rois, select_rois


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="formhtr", description="formHTR CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    p_process = sub.add_parser("process-logsheet", help="Extract values from a scanned logsheet to XLSX")
    p_process.add_argument("--pdf-logsheet", required=True, help="Scanned logsheet PDF")
    p_process.add_argument("--pdf-template", required=True, help="Template PDF")
    p_process.add_argument("--config-file", required=True, help="Config JSON")
    p_process.add_argument("--output-file", required=True, help="Output XLSX file")
    p_process.add_argument("--google", required=True, help="Path to Google Vision credentials JSON")
    p_process.add_argument("--amazon", required=True, help="Path to Amazon credentials JSON")
    p_process.add_argument("--azure", required=True, help="Path to Azure credentials JSON")
    p_process.add_argument("--debug", action=argparse.BooleanOptionalAction, default=False, help="Output annotated PDFs")
    p_process.add_argument("--backside", action=argparse.BooleanOptionalAction, default=False, help="Backside page present")
    p_process.add_argument("--backside-template", help="Backside template PDF")
    p_process.add_argument("--backside-config", help="Backside config JSON")
    p_process.add_argument(
        "--ugly-checkboxes",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Checkboxes have irregular shape / thick edges",
    )
    p_process.add_argument(
        "--aligned",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Scanned image already aligned with template (skip alignment)",
    )
    p_process.add_argument(
        "--filter-grayscale",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="During alignment keep only darkest grayscale pixels",
    )

    p_align = sub.add_parser("manual-align", help="Interactively align a scanned PDF to a template")
    p_align.add_argument("--pdf-template", required=True, help="Template PDF")
    p_align.add_argument("--pdf-logsheet", required=True, help="Scanned logsheet PDF")
    p_align.add_argument("--output", required=True, help="Output aligned PDF")
    p_align.add_argument("--backside-template", help="Backside template PDF")

    p_select = sub.add_parser("select-rois", help="Interactively define ROIs in a template PDF")
    p_select.add_argument("--pdf-file", required=True, help="Template PDF")
    p_select.add_argument("--output-file", required=True, help="Output config JSON")
    p_select.add_argument("--autodetect", action=argparse.BooleanOptionalAction, default=False)
    p_select.add_argument("--autodetect-filter", type=float, default=3)
    p_select.add_argument("--config-file", default=None, help="Existing config JSON to continue editing")
    p_select.add_argument("--detect-residuals", action=argparse.BooleanOptionalAction, default=False)
    p_select.add_argument("--credentials", default=None, help="Google credentials JSON (for residual detection)")
    p_select.add_argument("--display-residuals", action=argparse.BooleanOptionalAction, default=False)

    p_annot = sub.add_parser("annotate-rois", help="Interactively label ROI types/variables")
    p_annot.add_argument("--pdf-file", required=True, help="Template PDF")
    p_annot.add_argument("--config-file", required=True, help="Input config JSON")
    p_annot.add_argument("--output-file", required=True, help="Output config JSON")
    p_annot.add_argument("--remove-unannotated", action=argparse.BooleanOptionalAction, default=False)
    p_annot.add_argument("--display-residuals", action=argparse.BooleanOptionalAction, default=False)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "process-logsheet":
        if args.backside and (not args.backside_template or not args.backside_config):
            parser.error("--backside requires --backside-template and --backside-config.")

        credentials = load_credentials(
            google_credentials_path=args.google,
            amazon_credentials_path=args.amazon,
            azure_credentials_path=args.azure,
        )

        ratio = process_logsheet_to_xlsx(
            scanned_logsheet_pdf=args.pdf_logsheet,
            template_pdf=args.pdf_template,
            config_json=args.config_file,
            output_xlsx=args.output_file,
            credentials=credentials,
            debug=args.debug,
            backside=args.backside,
            backside_template_pdf=args.backside_template,
            backside_config_json=args.backside_config,
            ugly_checkboxes=args.ugly_checkboxes,
            already_aligned=args.aligned,
            filter_grayscale=args.filter_grayscale,
        )
        if ratio is not None:
            print(f"Success ratio: {ratio['ratio']:.3f}")
        return 0

    if args.command == "manual-align":
        manual_align_pdf(
            template_pdf=args.pdf_template,
            scanned_logsheet_pdf=args.pdf_logsheet,
            output_pdf=args.output,
            backside_template_pdf=args.backside_template,
        )
        return 0

    if args.command == "select-rois":
        if args.detect_residuals and not args.credentials:
            parser.error("--detect-residuals requires --credentials.")
        select_rois(
            template_pdf=args.pdf_file,
            output_config_json=args.output_file,
            autodetect=args.autodetect,
            autodetect_filter=args.autodetect_filter,
            existing_config_json=args.config_file,
            detect_residuals=args.detect_residuals,
            google_credentials_path=args.credentials,
            display_residuals=args.display_residuals,
        )
        return 0

    if args.command == "annotate-rois":
        annotate_rois(
            template_pdf=args.pdf_file,
            config_json=args.config_file,
            output_config_json=args.output_file,
            remove_unannotated=args.remove_unannotated,
            display_residuals=args.display_residuals,
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

