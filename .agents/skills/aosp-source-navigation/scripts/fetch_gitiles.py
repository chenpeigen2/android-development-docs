#!/usr/bin/env python3
"""Fetch a pinned Android Gitiles text file or tree, with source provenance.

Python standard library only. No clone, checkout, branch fallback, or device work.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

MAX_BYTES = 16 * 1024 * 1024


def relative_path(value: str, allow_empty: bool = False) -> str:
    if not value and allow_empty:
        return value
    if not value or value.startswith('/') or '\\' in value:
        raise ValueError('Use a relative POSIX path, not a URL or absolute path')
    if any(part in ('', '.', '..') for part in value.split('/')):
        raise ValueError('Empty, dot and parent path components are not allowed')
    if any(c in value for c in ('?', '#', ':')) or any(ord(c) < 32 for c in value):
        raise ValueError('Path must not contain URL query, fragment or control data')
    return value


def build_url(project: str, ref: str, path: str, kind: str) -> str:
    project = relative_path(project)
    if not (re.fullmatch(r'[0-9a-fA-F]{40}', ref) or
            (ref.startswith('refs/tags/') and relative_path(ref))):
        raise ValueError('Use refs/tags/<tag> or a full 40-character commit SHA')
    path = relative_path(path, allow_empty=kind == 'tree')
    if kind not in ('text', 'tree'):
        raise ValueError('kind must be text or tree')
    fmt = 'TEXT' if kind == 'text' else 'JSON'
    return ('https://android.googlesource.com/' + quote(project, safe='/') +
            '/+/' + quote(ref, safe='/') + '/' + quote(path, safe='/') +
            '?format=' + fmt)


def decode_payload(raw: bytes, kind: str) -> tuple[bytes, str | None]:
    if not raw:
        raise ValueError('Empty HTTP response is not source evidence')
    if kind == 'text':
        result = base64.b64decode(b''.join(raw.split()), validate=True)
        result.decode('utf-8')  # This helper intentionally excludes binary assets.
        return result, None
    payload = raw.decode('utf-8')
    if payload.startswith(")]}'"):
        payload = payload.partition('\n')[2]
    tree = json.loads(payload)
    if not isinstance(tree, dict) or not isinstance(tree.get('entries'), list):
        raise ValueError('Expected a Gitiles tree with entries, not an error page')
    return (json.dumps(tree, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), tree.get('id')


def fetch(project: str, ref: str, path: str, kind: str, cache_dir: Path,
          timeout: float = 60) -> dict:
    url = build_url(project, ref, path, kind)
    request = Request(url, headers={'User-Agent': 'aosp-source-navigation/1.0'})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Response exceeds 16 MiB; fetch a narrower target')
        status = response.status
    if status != 200:
        raise ValueError(f'Unexpected HTTP status: {status}')
    content, tree_id = decode_payload(raw, kind)
    digest = hashlib.sha256(content).hexdigest()
    # URL + content hash prevents cross-ref collisions and stale body/metadata pairs.
    key = hashlib.sha256(url.encode('utf-8')).hexdigest()[:20] + '-' + digest
    cache_dir = cache_dir.expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    body = cache_dir / (key + ('.source' if kind == 'text' else '.tree.json'))
    metadata = cache_dir / (key + '.evidence.json')
    evidence = dict(url=url, project=project, ref=ref, path=path, kind=kind,
                    fetched_at=datetime.now(timezone.utc).isoformat(), http_status=status,
                    sha256=digest, bytes=len(content), body=str(body), metadata=str(metadata))
    if tree_id:
        evidence['git_tree_id'] = tree_id
    body.write_bytes(content)
    metadata.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return evidence


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--project', required=True, help='e.g. platform/frameworks/base')
    cli.add_argument('--ref', required=True, help='refs/tags/<tag> or full commit SHA')
    cli.add_argument('--path', default='', help='Path relative to the Git project root')
    cli.add_argument('--kind', choices=['text', 'tree'], default='text')
    cli.add_argument('--cache-dir', type=Path, required=True)
    cli.add_argument('--timeout', type=float, default=60)
    args = cli.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError('timeout must be positive')
        result = fetch(args.project, args.ref, args.path, args.kind, args.cache_dir, args.timeout)
    except HTTPError as error:
        print(json.dumps({'error': str(error), 'http_status': error.code, 'url': error.url}), file=sys.stderr)
        return 2
    except (ValueError, OSError, URLError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
