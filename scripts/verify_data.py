#!/usr/bin/env python3
"""
驗證同步資料的完整性
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import SyncConfig


def verify_data(config: SyncConfig) -> bool:
    """驗證資料完整性"""
    print("正在驗證資料完整性...")

    errors = []

    # 檢查必要檔案
    required_files = ["release.txt", "OpenDataFilesList.csv"]
    for filename in required_files:
        filepath = config.data_path / filename
        if not filepath.exists():
            errors.append(f"缺少必要檔案：{filename}")

    # 檢查必要目錄（位於 Tables/ 下）
    required_dirs = ["MapingTables", "Properties"]
    for dirname in required_dirs:
        dirpath = config.tables_path / dirname
        if not dirpath.is_dir():
            errors.append(f"缺少必要目錄：Tables/{dirname}")
        elif not any(dirpath.iterdir()):
            errors.append(f"目錄為空：Tables/{dirname}")

    # 檢查 Properties/parts 目錄（由 CNS_component_word.zip 解壓縮）
    parts_dir = config.tables_path / "Properties" / "parts"
    if not parts_dir.is_dir():
        errors.append("缺少必要目錄：Tables/Properties/parts")
    elif not any(parts_dir.iterdir()):
        errors.append("目錄為空：Tables/Properties/parts")

    # 檢查元資料
    if not config.metadata_path.exists():
        errors.append("缺少元資料檔案")
    else:
        with open(config.metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)

        if not metadata.get("release_version"):
            errors.append("元資料缺少版本資訊")

    # 報告結果
    if errors:
        print("驗證失敗：")
        for error in errors:
            print(f"  - {error}")
        return False

    print("驗證通過：所有必要檔案和目錄皆存在")
    return True


def main() -> int:
    config = SyncConfig()
    success = verify_data(config)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
