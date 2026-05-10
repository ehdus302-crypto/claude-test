#!/usr/bin/env python3
"""
organize_files.py — 파일을 유형별 또는 날짜별로 정리합니다.

Usage:
  python3 organize_files.py <folder> --by-type        # 유형별 정리
  python3 organize_files.py <folder> --by-date <prefix> # 날짜별 정리 (중복 폴더 그룹)
  python3 organize_files.py <folder> --merge-groups <prefix> --output <name> # 날짜별 병합
  
  --dry-run  : 실제 이동 없이 계획만 출력
"""

import sys, os, re, unicodedata, shutil, argparse
from pathlib import Path
from datetime import datetime
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

def safe_dest(dest_dir, name):
    """충돌 시 _1, _2 ... 자동 부여."""
    dest = dest_dir / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    i = 1
    while True:
        dest = dest_dir / f"{stem}_{i}{suffix}"
        if not dest.exists():
            return dest
        i += 1

def by_type(folder, dry_run=False):
    folder = Path(folder)
    moved = defaultdict(int)
    skipped = []

    for item in list(folder.iterdir()):
        n = normalize(item.name)
        if n.startswith(".") or item.is_dir():
            continue
        ext = detect_ext(item.name)
        cat = EXT_TO_CAT.get(ext)
        
        # 이모지 등 특수 파일명 보조 판별
        if not cat:
            low = item.name.lower()
            if any(low.endswith(e) for e in [".jpg","jpeg",".png"]):
                cat = "이미지"
            elif any(low.endswith(e) for e in [".mp4",".mov"]):
                cat = "영상"

        if not cat:
            skipped.append(n)
            continue

        dest_dir = folder / cat
        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
        dest = safe_dest(dest_dir, item.name)
        
        if dry_run:
            print(f"  [이동 예정] {n} → {cat}/")
        else:
            shutil.move(str(item), str(dest))
        moved[cat] += 1

    return moved, skipped

def by_date(folder, prefix, output_name=None, dry_run=False):
    """
    prefix로 시작하는 폴더/파일을 날짜별로 묶습니다.
    예: prefix="SNS 운영", output_name="SNS_운영"
    """
    folder = Path(folder)
    prefix_nfc = normalize(prefix)
    output_name = output_name or prefix.replace(" ", "_")
    parent = folder / output_name

    moved = 0
    by_date_map = defaultdict(list)

    for item in folder.iterdir():
        n = normalize(item.name)
        if n == output_name or not n.startswith(prefix_nfc):
            continue

        # 날짜 추출: 타임스탬프 이름 또는 수정일 사용
        m = re.search(r'(\d{4}-\d{2}-\d{2})T', n)
        if m:
            date_str = m.group(1)
        else:
            mtime = item.stat().st_mtime
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        by_date_map[date_str].append(item)

    dates = sorted(by_date_map.keys())
    print(f"  '{prefix}' 그룹: {sum(len(v) for v in by_date_map.values())}개 항목, {len(dates)}개 날짜")

    for date_str, items in by_date_map.items():
        date_dir = parent / date_str
        if not dry_run:
            date_dir.mkdir(parents=True, exist_ok=True)
        for item in items:
            dest = safe_dest(date_dir, item.name)
            if dry_run:
                print(f"    [이동 예정] {normalize(item.name)} → {output_name}/{date_str}/")
            else:
                shutil.move(str(item), str(dest))
            moved += 1

    return moved

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("--by-type", action="store_true")
    parser.add_argument("--by-date", metavar="PREFIX")
    parser.add_argument("--output", metavar="OUTPUT_NAME")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.by_type:
        moved, skipped = by_type(args.folder, dry_run=args.dry_run)
        print("=== 유형별 정리 결과 ===")
        for cat, count in sorted(moved.items(), key=lambda x: -x[1]):
            print(f"  📁 {cat}: {count}개")
        if skipped:
            print(f"  미분류: {len(skipped)}개 (그대로 유지)")

    elif args.by_date:
        count = by_date(args.folder, args.by_date,
                        output_name=args.output, dry_run=args.dry_run)
        print(f"✅ 날짜별 정리: {count}개 이동 완료")

if __name__ == "__main__":
    main()
