"""Command-line interface for spotdl-lyrics-lora."""

import argparse
import sys
from spotdl_lyrics_lora.pipeline import (
    process_audio_file,
    process_folder,
    download_and_prepare,
)
from spotdl_lyrics_lora.dataset_validator import (
    validate_dataset_folder,
    print_validation_report,
)


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="spotdl-lora",
        description="Download and format song lyrics and metadata for ACE-Step 1.5 LoRA training.",
    )
    parser.add_argument("-d", "--dir", help="Directory containing audio files to process")
    parser.add_argument("-f", "--file", help="Single audio file to process")
    parser.add_argument("--download", help="Spotify URL or query to download via spotdl and process")
    parser.add_argument("-o", "--output", help="Optional output directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Generate .json & .caption.txt metadata")
    parser.add_argument("--auto-analyze", action="store_true", help="Zero-AI auto detection of BPM, key & caption")
    parser.add_argument("--use-ai", action="store_true", help="Use fast AI (Gemini/OpenAI/OpenRouter) for enrichment")
    parser.add_argument(
        "--ai-provider",
        default="auto",
        choices=["auto", "gemini", "openai", "openrouter"],
        help="AI provider (default: auto)",
    )
    parser.add_argument("--format", default="mp3", help="Audio format for downloads (default: mp3)")
    parser.add_argument("--validate", help="Validate a dataset folder for LoRA readiness and exit")
    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args()

    if args.validate:
        report = validate_dataset_folder(args.validate)
        print_validation_report(report)
        return

    json_flag = args.json or args.auto_analyze or args.use_ai

    if args.download:
        out_dir = args.output or "./downloaded"
        download_and_prepare(
            args.download,
            out_dir,
            args.format,
            args.overwrite,
            json_flag,
            args.auto_analyze,
            args.use_ai,
            args.ai_provider,
        )
    elif args.file:
        process_audio_file(
            args.file,
            args.output,
            args.overwrite,
            json_flag,
            args.auto_analyze,
            args.use_ai,
            args.ai_provider,
        )
    elif args.dir:
        process_folder(
            args.dir,
            args.output,
            args.overwrite,
            json_flag,
            args.auto_analyze,
            args.use_ai,
            args.ai_provider,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
