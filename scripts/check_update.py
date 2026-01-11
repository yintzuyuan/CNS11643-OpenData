#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 CNS11643 資料是否有更新
輸出 GitHub Actions outputs 供後續 job 使用
"""

import json
import os
import sys
from pathlib import Path

import requests

# 確保可以從不同位置執行時找到 config 模組
sys.path.insert(0, str(Path(__file__).parent))
from config import SyncConfig


def get_api_modified_date(config: SyncConfig) -> str:
    """從 API 取得最後修改日期"""
    response = requests.get(config.data_gov_api_url, timeout=30)
    response.raise_for_status()

    data = response.json()
    # API 回傳結構：{ result: { modifiedDate: "..." } }
    result = data.get('result', {})
    return result.get('modifiedDate', '')


def get_remote_release_version(config: SyncConfig) -> str:
    """從遠端 release.txt 取得版本號"""
    url = f"{config.cns11643_base_url}/release.txt"
    # 官網 SSL 憑證有問題，需禁用驗證
    response = requests.get(url, timeout=30, verify=False)
    response.raise_for_status()

    # 解碼為 UTF-8 with BOM
    text = response.content.decode('utf-8-sig')

    # 解析版本號（格式：版本：20250718 或 版本:20250718）
    for line in text.splitlines():
        if '版本：' in line or '版本:' in line:
            parts = line.split('：') if '：' in line else line.split(':')
            if len(parts) >= 2:
                return parts[1].strip()

    return ''


def get_current_metadata(config: SyncConfig) -> dict:
    """讀取本地元資料"""
    if config.metadata_path.exists():
        with open(config.metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def set_github_output(name: str, value: str) -> None:
    """設定 GitHub Actions output"""
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"{name}={value}\n")
    else:
        # 本地測試時輸出到 stdout
        print(f"::set-output name={name}::{value}")


def main() -> int:
    config = SyncConfig()

    print("正在檢查 CNS11643 資料更新...")

    # 取得遠端資訊
    try:
        api_modified_date = get_api_modified_date(config)
        remote_version = get_remote_release_version(config)
    except Exception as e:
        print(f"錯誤：無法取得遠端資訊 - {e}")
        set_github_output('has_update', 'false')
        return 1

    print(f"遠端 API 修改日期：{api_modified_date}")
    print(f"遠端 release 版本：{remote_version}")

    # 取得本地資訊
    metadata = get_current_metadata(config)
    current_version = metadata.get('release_version', '')
    current_api_date = metadata.get('api_modified_date', '')

    print(f"本地 release 版本：{current_version or '(無)'}")
    print(f"本地 API 修改日期：{current_api_date or '(無)'}")

    # 判斷是否需要更新
    has_update = False

    if config.force_download:
        print("強制下載模式已啟用")
        has_update = True
    elif not current_version:
        print("首次同步")
        has_update = True
    elif api_modified_date != current_api_date:
        print("API 修改日期已變更")
        has_update = True
    elif remote_version != current_version:
        print("release 版本已變更")
        has_update = True
    else:
        print("資料已是最新版本")

    # 設定 outputs
    set_github_output('has_update', str(has_update).lower())
    set_github_output('new_version', remote_version)
    set_github_output('current_version', current_version)
    set_github_output('api_modified_date', api_modified_date)

    return 0


if __name__ == '__main__':
    sys.exit(main())
