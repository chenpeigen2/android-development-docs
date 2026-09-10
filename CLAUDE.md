# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese documentation repository for Android development knowledge. It contains comprehensive technical documents covering Android fundamentals, core mechanisms, performance optimization, third-party libraries, cross-platform development, and security.

## Document Structure

All documents are in Chinese and follow these naming conventions:
- `Android_[Topic]详解.md` - Detailed explanations
- `Android_[Topic]完全指南.md` - Complete guides
- `[Framework]_完全指南.md` - Cross-platform framework guides

### Categories and Inventory

`README.md` is the source of truth for the ordered catalog, document counts,
file sizes, and update history. Categories include fundamentals, core mechanisms,
Framework internals, performance, architecture, libraries, cross-platform,
build/debugging tools, data processing, dependency injection, security, display,
and supplementary source/internal-framework guides. Do not reuse the old six-category
inventory or count review records and contributor instructions as technical guides.

Structural checks: install `tools/requirements-docs.txt` and run
`python tools/check_docs.py`. The optional `--fix-toc` rebuilds existing opening TOCs
from real headings, without creating missing technical chapters. A passing structural
check is not evidence that all API facts or code examples were source-verified.

## Adding New Documents

1. Create the markdown file with appropriate naming convention
2. Update `README.md`:
   - Add entry to the relevant category table
   - Update document statistics (count, total size)
   - Add entry to update log with date
3. Commit with message format: `docs: [description]`

## Document Content Standards

Documents typically include:
- ASCII diagrams and code structure visualizations
- Source code analysis with file paths (e.g., `frameworks/base/...`)
- Chapter-based organization (typically 10-20 chapters)
- Interview questions section at the end
- Practical examples and code snippets

## Git Conventions

- Commit messages use Chinese: `docs: [description]`
- Example: `docs: 新增 Android 安全详解文档 (120KB, 18章, 3730行)`
- Main branch: `main`
- Remote: `origin/main`
