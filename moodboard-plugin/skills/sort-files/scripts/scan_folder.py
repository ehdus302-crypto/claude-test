#!/usr/bin/env python3
"""
scan_folder.py — 폴더 현황을 스캔하고 정리 계획을 출력합니다.
Usage: python3 scan_folder.py <folder_path>
"""

import os, sys, unicodedata, re
from pathlib import Path
from collections import defaultdict

CATEGORY_MAP = {
    "이미지":      [".png", ".jpg", ".jpeg", ".heic", ".webp", ".gif", ".bmp",
                    ".tiff", ".tif", ".svg", ".ico", ".raw", ".cr2", ".nef"],
    "영상":        [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".m4v",
                    ".webm", ".mpg", ".mpeg", ".3gp"],
    "음악":        [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma",
                    ".aiff", ".opus"],
    "문서":        [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
                    ".txt", ".md", ".html", ".htm", ".csv", ".tsv", ".rtf", ".eml"],
    "디자인":      [".psd", ".ai", ".eps", ".sketch", ".fig", ".xd", ".prfpset",
                    ".otf", ".ttf", ".woff", ".woff2", ".prproj"],
    "압축":        [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".dmg"],
    "앱_설치파일": [".pkg", ".exe", ".sh", ".app", ".deb", ".rpm", ".msi", ".xapk"],
    "데이터":      [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"],
    "코드":        [".py", ".js", ".ts", ".swift", ".kt", ".java", ".c", ".cpp",
                    ".go", ".rs", ".rb", ".php", ".css", ".scss"],
}

EXT_TO_CAT = {ext: cat for cat, exts in CATEGORY_MAP.items() for ext in exts}

def normalize(s):
    return unicodedata.normalize("NFC", s)

def detect_ext(name):
    ext = Path(name).suffix.lower()
    if not ext:
        for candidate in [".jpg", ".jpeg", ".png", ".mp4", ".mov", ".pdf"]:
            if name.lower().endswith(candidate):
                return candidate
    return ext

def human_size(b):
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"

def scan(folder):
    folder = Path(folder)
    by_cat = defaultdict(list)
    unclassified = []
    dirs = []
    total_size = 0

    for item in folder.iterdir():
        n = normalize(item.name)
        if n.startswith("."): continue
        if item.is_dir():
            dirs.append(item); continue
        ext = detect_ext(item.name)
        cat = EXT_TO_CAT.get(ext)
        size = item.stat().st_size
        total_size += size
        if cat:
            by_cat[cat].append((n, size))
        else:
            unclassified.append((n, size, ext))

    # 중복 폴더 그룹 감지
    base_names = defaultdict(list)
    for d in dirs:
        n = normalize(d.name)
        base = re.sub(r'\s*\(\d+\)(\s+\d+)?$', '', n).strip()
        base = re.sub(r'\s*-\s*\d{4}-\d{2}-\d{2}T.*$', '', base).strip()
        base = re.sub(r'\s+\d+$', '', base).strip()
        base_names[base].append(d)

    dup_groups = {k: v for k, v in base_names.items() if len(v) > 2}
    return by_cat, unclassified, dirs, dup_groups, total_size

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"📂 스캔: {folder}\n")
    by_cat, unclassified, dirs, dup_groups, total_size = scan(folder)

    print(f"=== 파일 ({human_size(total_size)}) ===")
    for cat, files in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        cat_size = sum(s for _, s in files)
        print(f"  {cat:12s}: {len(files):4d}개  ({human_size(cat_size)})")
    if unclassified:
        print(f"  {'미분류':12s}: {len(unclassified):4d}개")

    print(f"\n=== 폴더 ({len(dirs)}개) ===")
    if dup_groups:
        print("  ⚠️  중복 폴더 그룹 감지:")
        for base, members in list(dup_groups.items())[:8]:
            print(f"    '{base}' → {len(members)}개 버전")
    else:
        print("  중복 그룹 없음")

if __name__ == "__main__":
    main()
