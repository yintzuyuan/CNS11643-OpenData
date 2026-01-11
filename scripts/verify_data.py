#!/usr/bin/env python3
"""
驗證同步資料的完整性

驗證層級：
- L1：目錄結構驗證 - 確認必要目錄存在
- L2：關鍵檔案驗證 - 確認重要對照表和屬性檔案存在
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import SyncConfig

# L1：必要目錄結構
REQUIRED_DIRECTORIES = [
    "Tables/MapingTables",
    "Tables/MapingTables/Big5",
    "Tables/MapingTables/Unicode",
    "Tables/MapingTables/地政",
    "Tables/Properties",
    "Tables/Properties/parts",
]

# L2：關鍵檔案（相對於專案根目錄）
REQUIRED_FILES = [
    # 基本資訊
    "release.txt",
    "OpenDataFilesList.csv",
    # Big5 對照表
    "Tables/MapingTables/Big5/CNS2BIG5.txt",
    # Unicode 對照表
    "Tables/MapingTables/Unicode/CNS2UNICODE_Unicode BMP.txt",
    # 其他對照表（公路監理、稅務、工商、金融）
    "Tables/MapingTables/CNS2DCI.txt",
    "Tables/MapingTables/CNS2TAX.txt",
    "Tables/MapingTables/CNS2INC.txt",
    "Tables/MapingTables/CNS2FIN.txt",
    # 屬性資料
    "Tables/Properties/CNS_phonetic.txt",
    "Tables/Properties/CNS_radical.txt",
    "Tables/Properties/CNS_stroke.txt",
    "Tables/Properties/CNS_cangjie.txt",
]


def verify_directories(base_path: Path) -> list[str]:
    """L1：驗證目錄結構"""
    errors = []
    for dir_path in REQUIRED_DIRECTORIES:
        full_path = base_path / dir_path
        if not full_path.is_dir():
            errors.append(f"缺少必要目錄：{dir_path}")
        elif not any(full_path.iterdir()):
            errors.append(f"目錄為空：{dir_path}")
    return errors


def verify_files(base_path: Path) -> list[str]:
    """L2：驗證關鍵檔案"""
    errors = []
    for file_path in REQUIRED_FILES:
        full_path = base_path / file_path
        if not full_path.is_file():
            errors.append(f"缺少必要檔案：{file_path}")
        elif full_path.stat().st_size == 0:
            errors.append(f"檔案為空：{file_path}")
    return errors


def verify_metadata(config: SyncConfig) -> list[str]:
    """驗證元資料檔案"""
    errors = []
    if not config.metadata_path.exists():
        errors.append("缺少元資料檔案：sync_metadata.json")
    else:
        with open(config.metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)
        if not metadata.get("release_version"):
            errors.append("元資料缺少版本資訊")
    return errors


def verify_data(config: SyncConfig, skip_metadata: bool = False) -> bool:
    """
    驗證資料完整性

    Args:
        config: 同步設定
        skip_metadata: 是否跳過元資料驗證（用於 CI 檢查現有資料）

    Returns:
        驗證是否通過
    """
    print("正在驗證資料完整性...")
    print(f"  資料路徑：{config.data_path}")

    all_errors = []

    # L1：目錄結構驗證
    print("\n[L1] 驗證目錄結構...")
    dir_errors = verify_directories(config.data_path)
    all_errors.extend(dir_errors)
    if dir_errors:
        for error in dir_errors:
            print(f"  ✗ {error}")
    else:
        print(f"  ✓ {len(REQUIRED_DIRECTORIES)} 個目錄結構正確")

    # L2：關鍵檔案驗證
    print("\n[L2] 驗證關鍵檔案...")
    file_errors = verify_files(config.data_path)
    all_errors.extend(file_errors)
    if file_errors:
        for error in file_errors:
            print(f"  ✗ {error}")
    else:
        print(f"  ✓ {len(REQUIRED_FILES)} 個關鍵檔案存在")

    # 元資料驗證（可選）
    if not skip_metadata:
        print("\n[Meta] 驗證元資料...")
        meta_errors = verify_metadata(config)
        all_errors.extend(meta_errors)
        if meta_errors:
            for error in meta_errors:
                print(f"  ✗ {error}")
        else:
            print("  ✓ 元資料完整")

    # 報告結果
    print()
    if all_errors:
        print(f"驗證失敗：發現 {len(all_errors)} 個問題")
        return False

    print("驗證通過：所有必要檔案和目錄皆存在")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="驗證 CNS11643 資料完整性")
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="跳過元資料驗證（用於 CI 檢查現有資料）",
    )
    args = parser.parse_args()

    config = SyncConfig()
    success = verify_data(config, skip_metadata=args.skip_metadata)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
