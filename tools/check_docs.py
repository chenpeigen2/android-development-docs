#!/usr/bin/env python3
"""Check local Markdown references and fences; optionally render or rebuild TOCs.

Install: python -m pip install -r tools/requirements-docs.txt
Check:   python tools/check_docs.py --json <path> --render-dir <outside-repo-dir>
TOCs:    python tools/check_docs.py --fix-toc

No external URLs are fetched. --fix-toc changes only the opening TOC, never body
headings or missing chapters. Passing structural checks does not verify API facts.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

EXCLUDED = {'.git', '.idea', 'build', '.venv', 'node_modules', '__pycache__'}


def slug(title: str) -> str:
    title = re.sub(r'<[^>]*>', '', title).strip().lower()
    return ''.join(c for c in title if c in '-_ ' or
                   unicodedata.category(c)[0] in 'LN').replace(' ', '-')


def parse_document(text: str):
    parser = MarkdownIt('commonmark', {'html': True}).enable('table')
    tokens = parser.parse(text)
    headings, anchors, used, issues = [], set(), set(), []
    lines = text.splitlines()
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            inline = tokens[i + 1]
            title = ''.join(c.content for c in inline.children or []
                            if c.type in ('text', 'code_inline', 'html_inline'))
            base = slug(title)
            anchor, number = base, 0
            while anchor in used:
                number += 1
                anchor = f'{base}-{number}'
            used.add(anchor)
            anchors.add(anchor)
            token.attrSet('id', anchor)
            headings.append({'title': title, 'inline': inline.content,
                             'level': int(token.tag[1:]), 'anchor': anchor,
                             'start': token.map[0], 'end': token.map[1]})
        if token.type in ('html_block', 'inline'):
            anchors.update(re.findall(r'\b(?:id|name)=["\x27]([^"\x27]+)', token.content))
        if token.type == 'fence' and token.map:
            last = lines[token.map[1] - 1].strip()
            closing = re.fullmatch(re.escape(token.markup[0]) +
                                   '{' + str(len(token.markup)) + r',}\s*', last)
            if not closing or token.map[1] - token.map[0] < 2:
                issues.append({'kind': 'unclosed_fence', 'line': token.map[0] + 1})
            if not token.info.strip():
                issues.append({'kind': 'missing_fence_language', 'line': token.map[0] + 1})
    return parser, tokens, headings, anchors, issues


def rebuild_toc(text: str) -> str:
    _, _, headings, _, _ = parse_document(text)
    # Only replace an explicit opening TOC. Don't invent sections in other files.
    toc = next((h for h in headings if h['level'] == 2 and
                h['title'].replace('📚', '').strip() in ('目录', '目 录')), None)
    if toc is None:
        return text
    body = next((h for h in headings if h['start'] > toc['start'] and
                 h['level'] <= 2), None)
    if body is None:
        return text
    lines = text.splitlines(keepends=True)
    # Old TOCs can contain H3 group headings. Remove them before allocating
    # duplicate slugs, otherwise removed headings leave stale '-1' targets.
    prefix = ''.join(lines[:toc['end']]) + '\n'
    suffix = ''.join(lines[body['start']:])
    retained = parse_document(prefix + suffix)[2]
    body_start = len(prefix.splitlines())
    entries = []
    for heading in retained:
        if heading['start'] < body_start or not 2 <= heading['level'] <= 4:
            continue
        label = heading['inline'].replace('[', r'\[').replace(']', r'\]')
        entries.append('  ' * (heading['level'] - 2) +
                       f"- [{label}](#{heading['anchor']})\n")
    return ''.join(lines[:toc['end']]) + '\n' + ''.join(entries) + '\n---\n\n' + \
        ''.join(lines[body['start']:])


def check(root: Path, fix_toc: bool = False, render_dir: Path | None = None):
    root = root.resolve()
    paths = sorted(p for p in root.rglob('*.md')
                   if not (set(p.relative_to(root).parts) & EXCLUDED))
    documents, changed = {}, []
    for path in paths:
        text = path.read_text(encoding='utf-8-sig')
        if fix_toc:
            updated = rebuild_toc(text)
            if updated != text:
                path.write_text(updated, encoding='utf-8')
                changed.append(path.relative_to(root).as_posix())
                text = updated
        documents[path.resolve()] = (text, parse_document(text))
    all_issues = []
    counts = Counter()
    for path, (text, parsed) in documents.items():
        parser, tokens, headings, anchors, issues = parsed
        issues = list(issues)
        counts['headings'] += len(headings)
        counts['fences'] += sum(t.type == 'fence' for t in tokens)
        counts['tables'] += sum(t.type == 'table_open' for t in tokens)
        for token in tokens:
            for child in token.children or []:
                href = (child.attrGet('href') if child.type == 'link_open' else
                        child.attrGet('src') if child.type == 'image' else None)
                if not href or urlsplit(href).scheme or href.startswith('//'):
                    continue
                counts['local_references'] += 1
                dest = urlsplit(href)
                target = (path.parent / unquote(dest.path)).resolve() if dest.path else path
                issue = {'line': token.map[0] + 1 if token.map else 0, 'target': href}
                if not target.exists():
                    issues.append(dict(issue, kind='missing_file'))
                elif dest.fragment and target.suffix.lower() == '.md':
                    other = documents.get(target)
                    if other is None:
                        # Do not silently skip Markdown targets outside the inventory.
                        try:
                            other = ('', parse_document(target.read_text(encoding='utf-8-sig')))
                        except (OSError, UnicodeError):
                            issues.append(dict(issue, kind='unreadable_target'))
                            continue
                    if unquote(dest.fragment) not in other[1][3]:
                        issues.append(dict(issue, kind='missing_anchor'))
        for issue in issues:
            all_issues.append(dict(issue, file=path.relative_to(root).as_posix()))
        if render_dir:
            render_dir.mkdir(parents=True, exist_ok=True)
            dest = render_dir / (path.relative_to(root).as_posix().replace('/', '__') + '.html')
            # Render the parsed tokens with the same heading IDs used by the checker.
            content = parser.renderer.render(tokens, parser.options, {})
            dest.write_text('<!doctype html><meta charset="utf-8"><title>' +
                            html.escape(path.name) + '</title>' + content, encoding='utf-8')
    return {'documents': len(paths), 'counts': dict(counts),
            'toc_updated': changed, 'issues': all_issues}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument('--fix-toc', action='store_true')
    cli.add_argument('--json', type=Path)
    cli.add_argument('--render-dir', type=Path)
    args = cli.parse_args()
    report = check(args.root.resolve(), args.fix_toc, args.render_dir)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"documents={report['documents']} issues={len(report['issues'])} "
          f"toc_updated={len(report['toc_updated'])} counts={report['counts']}")
    for issue in report['issues']:
        print(f"{issue['file']}:{issue['line']}: {issue['kind']} {issue.get('target', '')}")
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    sys.exit(main())
