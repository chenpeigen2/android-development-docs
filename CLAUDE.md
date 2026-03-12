# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese documentation repository for Android development knowledge. It contains comprehensive technical documents covering Android fundamentals, core mechanisms, performance optimization, third-party libraries, cross-platform development, and security.

## Document Structure

All documents are in Chinese and follow these naming conventions:
- `Android_[Topic]详解.md` - Detailed explanations
- `Android_[Topic]完全指南.md` - Complete guides
- `[Framework]_完全指南.md` - Cross-platform framework guides

### Categories (6 major sections)

1. **基础知识** (9 docs): View drawing, event distribution, animations, Activity, components, screen adaptation, networking
2. **核心机制** (8 docs): Binder, Handler, VM, ClassLoader, Zygote/SystemServer, AndroidX, architecture patterns, background tasks
3. **性能优化** (4 docs): Performance, memory leaks, ANR, Systrace
4. **三方库详解** (2 docs): Glide/Fresco/MMKV/PAG/Lottie, OkHttp/Retrofit
5. **跨平台开发** (3 docs): Flutter, React Native, Jetpack Compose
6. **安全与防护** (1 doc): Obfuscation, hardening, encryption, network security

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
