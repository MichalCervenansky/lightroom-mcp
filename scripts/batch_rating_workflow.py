#!/usr/bin/env python3
"""
Optimized Photo Rating Workflow for Lightroom MCP

This script minimizes tokens and MCP calls by:
1. Extracting all previews locally upfront (no MCP calls)
2. Calculating localIds from filename patterns (no lookup calls)
3. Batching photos by rating and applying in single MCP calls

Usage:
    python batch_rating_workflow.py /path/to/raw/folder

The script will:
1. Extract previews to /tmp/lr_previews/
2. Output a JSON file with filename->rating mappings
3. Generate MCP commands to batch-apply ratings
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    import rawpy
    from PIL import Image
    import io
except ImportError:
    print("Required packages: pip install rawpy pillow")
    sys.exit(1)


RAW_EXTENSIONS = {'.raf', '.cr2', '.cr3', '.nef', '.arw', '.dng', '.rw2', '.orf'}
PREVIEW_OUTPUT_DIR = Path("/tmp/lr_previews")
PREVIEW_SIZE = (800, 800)


def extract_previews(raw_folder: Path, output_dir: Path = PREVIEW_OUTPUT_DIR) -> list[str]:
    """
    Extract embedded JPEGs from all RAW files in a folder.

    This bypasses MCP entirely - much faster and more reliable than
    using Lightroom's preview generation.

    Returns list of successfully extracted filenames (without extension).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_files = sorted([
        f for f in raw_folder.iterdir()
        if f.suffix.lower() in RAW_EXTENSIONS
    ])

    print(f"Found {len(raw_files)} RAW files in {raw_folder}")

    extracted = []
    for i, raw_path in enumerate(raw_files):
        try:
            raw = rawpy.imread(str(raw_path))
            thumb = raw.extract_thumb()
            raw.close()

            if thumb.format == rawpy.ThumbFormat.JPEG:
                img = Image.open(io.BytesIO(thumb.data))
                img.thumbnail(PREVIEW_SIZE)

                stem = raw_path.stem
                out_path = output_dir / f"{stem}.jpg"
                img.save(out_path, 'JPEG', quality=85)
                extracted.append(stem)

            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{len(raw_files)}")

        except Exception as e:
            print(f"Error extracting {raw_path.name}: {e}")

    print(f"Extracted {len(extracted)}/{len(raw_files)} previews to {output_dir}")
    return extracted


def calculate_local_id(filename: str, base_filename: str, base_local_id: int) -> int:
    """
    Calculate Lightroom localId from filename pattern.

    Lightroom assigns sequential localIds during import. If you know the
    localId of one file, you can calculate others based on file order.

    This eliminates the need for find_photo_by_filename MCP calls.

    Args:
        filename: Target filename (e.g., "DSCF4022")
        base_filename: Known filename (e.g., "DSCF3987")
        base_local_id: Known localId for base_filename

    Returns:
        Calculated localId for target filename
    """
    # Extract numeric parts
    base_num = int(''.join(filter(str.isdigit, base_filename)))
    target_num = int(''.join(filter(str.isdigit, filename)))

    # Calculate offset, accounting for any gaps in numbering
    # For Fuji cameras, there's no frame 4000 (skips from 3999 to 4001)
    offset = target_num - base_num

    # Adjust for known gaps (customize based on your camera)
    if base_num < 4000 <= target_num:
        offset -= 1  # Account for missing 4000

    return base_local_id + offset


def generate_batch_commands(ratings: dict[str, int], base_filename: str, base_local_id: int) -> dict[int, list[int]]:
    """
    Group photos by rating and generate batch select commands.

    Instead of calling select_photos + set_rating for each photo (2N calls),
    we group by rating and apply once per rating level (2*5 = 10 calls max).

    Args:
        ratings: Dict mapping filename stems to ratings (e.g., {"DSCF3987": 3})
        base_filename: Known filename for localId calculation
        base_local_id: Known localId

    Returns:
        Dict mapping rating -> list of localIds
    """
    by_rating = {1: [], 2: [], 3: [], 4: [], 5: []}

    for filename, rating in ratings.items():
        if rating < 1 or rating > 5:
            continue
        local_id = calculate_local_id(filename, base_filename, base_local_id)
        by_rating[rating].append(local_id)

    # Remove empty ratings
    return {r: ids for r, ids in by_rating.items() if ids}


def save_ratings(ratings: dict[str, int], output_path: Path):
    """Save ratings to JSON for later application."""
    with open(output_path, 'w') as f:
        json.dump(ratings, f, indent=2)
    print(f"Saved {len(ratings)} ratings to {output_path}")


def load_ratings(input_path: Path) -> dict[str, int]:
    """Load ratings from JSON."""
    with open(input_path) as f:
        return json.load(f)


def print_mcp_commands(batch_commands: dict[int, list[int]]):
    """
    Print the MCP commands needed to apply ratings.

    These can be copy-pasted or used programmatically.
    """
    print("\n" + "="*60)
    print("MCP COMMANDS TO APPLY RATINGS")
    print("="*60)

    total_calls = 0
    for rating in sorted(batch_commands.keys(), reverse=True):
        local_ids = batch_commands[rating]
        print(f"\n# {rating}-star ({len(local_ids)} photos)")
        print(f"select_photos(photo_ids={local_ids})")
        print(f"set_rating(rating={rating})")
        total_calls += 2

    print(f"\n# Total MCP calls: {total_calls}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Batch photo rating workflow")
    parser.add_argument("raw_folder", help="Path to folder with RAW files")
    parser.add_argument("--base-filename", default="DSCF3987",
                        help="Known filename for localId calculation")
    parser.add_argument("--base-local-id", type=int, default=1022008,
                        help="Known localId for base filename")
    parser.add_argument("--ratings-file", type=Path,
                        help="JSON file with existing ratings to apply")
    parser.add_argument("--extract-only", action="store_true",
                        help="Only extract previews, don't generate commands")

    args = parser.parse_args()
    raw_folder = Path(args.raw_folder)

    if not raw_folder.exists():
        print(f"Error: Folder not found: {raw_folder}")
        sys.exit(1)

    # Step 1: Extract previews
    print("\n[Step 1] Extracting previews...")
    extracted = extract_previews(raw_folder)

    if args.extract_only:
        print("\nPreviews extracted. Use Claude to rate them, then run again with --ratings-file")
        return

    # Step 2: Load or create ratings
    if args.ratings_file and args.ratings_file.exists():
        print(f"\n[Step 2] Loading ratings from {args.ratings_file}...")
        ratings = load_ratings(args.ratings_file)
    else:
        print("\n[Step 2] No ratings file provided.")
        print("Have Claude rate the previews in /tmp/lr_previews/")
        print("Save ratings as JSON: {\"DSCF3987\": 3, \"DSCF3988\": 4, ...}")
        print("Then run again with --ratings-file ratings.json")
        return

    # Step 3: Generate batch commands
    print("\n[Step 3] Generating batch commands...")
    batch_commands = generate_batch_commands(
        ratings,
        args.base_filename,
        args.base_local_id
    )

    # Print summary
    print("\nRATINGS SUMMARY:")
    for rating in sorted(batch_commands.keys(), reverse=True):
        print(f"  {rating} stars: {len(batch_commands[rating])} photos")

    # Print MCP commands
    print_mcp_commands(batch_commands)


if __name__ == "__main__":
    main()
