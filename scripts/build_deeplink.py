#!/usr/bin/env python3
"""Build HAPP deeplink from JSON config.

Reads HAPP/default.json, minifies it, base64-url-safe encodes and writes
HAPP/default.deeplink in `happ://routing/onadd/<base64>` format.

Used by the GitHub Action on every push to keep .deeplink in sync with .json.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path


def build_deeplink(json_path: Path, deeplink_path: Path) -> tuple[int, int]:
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    minified = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    encoded = base64.urlsafe_b64encode(minified.encode('utf-8')).decode('ascii').rstrip('=')
    deeplink = f'happ://routing/onadd/{encoded}'

    deeplink_path.parent.mkdir(parents=True, exist_ok=True)
    deeplink_path.write_text(deeplink, encoding='utf-8')

    return len(minified), len(deeplink)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build HApp routing deeplink from JSON config.')
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('HAPP/default.json'),
        help='Path to JSON config (default: HAPP/default.json)',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('HAPP/default.deeplink'),
        help='Path to write deeplink (default: HAPP/default.deeplink)',
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f'ERROR: input not found: {args.input}', file=sys.stderr)
        return 1

    json_size, deeplink_size = build_deeplink(args.input, args.output)
    print(f'OK: {args.input} ({json_size} bytes) -> {args.output} ({deeplink_size} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
