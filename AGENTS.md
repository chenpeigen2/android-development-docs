# Repository Guidelines

## Project Structure & Module Organization

This repository is a Chinese-language Android development documentation set, not an executable Android project. Topic guides are Markdown files in the repository root, organized conceptually into fundamentals, core mechanisms, performance, architecture, libraries, cross-platform development, and security. Framework internals are grouped under `framework/` (for example, `framework/Android_AMS_深度解析.md`). `README.md` is the catalog and update history; keep it synchronized with every document addition or substantial revision. `CLAUDE.md` records the existing content and Git conventions.

## Build, Test, and Development Commands

There is no compilation or runtime build. Use a Markdown-capable editor for authoring, then inspect changes with:

```powershell
git diff --check
git diff --stat
```

Before submitting, verify links and headings with the repository’s Markdown preview or a Markdown linter available in your environment. A simple inventory check is `Get-ChildItem -Recurse -Filter *.md`.

## Coding Style & Naming Conventions

Use UTF-8 Markdown with clear `#`/`##` chapter hierarchy, short paragraphs, and fenced code blocks with language tags such as ` ```kotlin ` or ` ```bash `. Preserve Chinese terminology and use English API/class names exactly as they appear in Android or AOSP source. Name new files using the established patterns, such as `Android_[主题]详解.md` or `Android_[主题]完全指南.md`; use descriptive Chinese names and avoid unexplained abbreviations. Prefer ASCII diagrams and cite concrete AOSP paths, versions, and commands when discussing implementation details.

## Testing Guidelines

Treat documentation review as testing: render changed Markdown, check code snippets for syntax errors when practical, and verify internal links, anchors, tables, and image references. For source-analysis updates, confirm referenced classes and paths against the stated Android/AOSP version. No formal coverage threshold exists, but every new or substantially changed guide should receive a manual proofread.

## Commit & Pull Request Guidelines

Use the observed `docs:` prefix and a concise, specific description, e.g. `docs: 新增 Android 安全详解文档`. Pull requests should explain the topic and scope, list affected files, note link/rendering checks, and update `README.md` statistics and changelog entries. Include screenshots only when they clarify rendered layout or diagrams. Keep unrelated edits out of the change.
