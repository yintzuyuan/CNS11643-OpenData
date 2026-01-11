#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNS11643 資料同步腳本
下載、解壓縮、驗證資料完整性
"""

import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import SyncConfig


class CNS11643Syncer:
    """CNS11643 資料同步器"""

    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CNS11643-OpenData-Syncer/1.0'
        })

    def sync(self) -> bool:
        """執行完整同步流程"""
        print("開始同步 CNS11643 資料...")

        # 確保目標目錄存在
        self.config.data_path.mkdir(parents=True, exist_ok=True)

        # 讀取現有元資料
        metadata = self._load_metadata()

        # 下載並處理每個檔案
        downloaded_files = {}
        for filename in self.config.sync_files:
            result = self._download_and_process(filename)
            if result:
                downloaded_files[filename] = result
            else:
                print(f"警告：{filename} 下載或處理失敗")

        if not downloaded_files:
            print("錯誤：沒有成功下載任何檔案")
            return False

        # 更新元資料
        self._update_metadata(metadata, downloaded_files)

        print(f"同步完成，共處理 {len(downloaded_files)} 個檔案")
        return True

    def _download_and_process(self, filename: str) -> Optional[Dict]:
        """下載並處理單一檔案"""
        url = f"{self.config.cns11643_base_url}/{filename}"
        local_path = self.config.data_path / filename

        print(f"正在下載：{filename}")

        try:
            # 官網 SSL 憑證有問題，需禁用驗證
            response = self.session.get(
                url,
                timeout=self.config.download_timeout,
                stream=True,
                verify=False
            )
            response.raise_for_status()

            # 計算 SHA256 同時寫入檔案
            sha256 = hashlib.sha256()
            total_size = 0

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        sha256.update(chunk)
                        total_size += len(chunk)

            file_info = {
                'sha256': sha256.hexdigest(),
                'size': total_size,
                'downloaded_at': datetime.now(timezone.utc).isoformat()
            }

            # 如果是 ZIP 檔案，解壓縮到 Tables/ 目錄
            if filename.endswith('.zip'):
                # MapingTables.zip → Tables/MapingTables/
                # Properties.zip → Tables/Properties/
                extract_dir = self.config.tables_path / filename.replace('.zip', '')
                self._extract_zip(local_path, extract_dir)
                # 解壓縮後刪除 ZIP 檔案（節省空間）
                local_path.unlink()

                # 處理巢狀 ZIP 檔案（Properties 內的 CNS_component_word.zip）
                if filename == 'Properties.zip':
                    self._extract_nested_zips(extract_dir)

            print(f"  完成：{self._format_size(total_size)}")
            return file_info

        except Exception as e:
            print(f"  錯誤：{e}")
            return None

    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> None:
        """解壓縮 ZIP 檔案，正確處理 Big5 編碼的檔名"""
        # 清除舊目錄
        if extract_dir.exists():
            shutil.rmtree(extract_dir)

        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                # 修正檔名編碼：CP437 → Big5
                try:
                    # Python zipfile 將非 UTF-8 檔名解碼為 CP437
                    # 需要還原為 bytes 再用 Big5 解碼
                    filename_bytes = info.filename.encode('cp437')
                    correct_filename = filename_bytes.decode('big5')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    # 如果轉換失敗，使用原始檔名
                    correct_filename = info.filename

                # 建立目標路徑
                target_path = extract_dir / correct_filename

                # 如果是目錄，建立目錄
                if info.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    # 確保父目錄存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    # 解壓縮檔案
                    with zf.open(info) as src, open(target_path, 'wb') as dst:
                        dst.write(src.read())

        print(f"  已解壓縮至：{extract_dir}/")

    def _extract_nested_zips(self, parent_dir: Path) -> None:
        """處理目錄內的巢狀 ZIP 檔案"""
        # CNS_component_word.zip 內部已有 parts/ 目錄結構
        # 直接解壓縮到 parent_dir，ZIP 內的 parts/ 會自動建立
        nested_zips = ['CNS_component_word.zip']

        for zip_name in nested_zips:
            zip_path = parent_dir / zip_name
            if zip_path.exists():
                print(f"  處理巢狀壓縮檔：{zip_name}")
                self._extract_nested_zip_preserve_structure(zip_path, parent_dir)
                # 解壓縮後刪除巢狀 ZIP 檔案
                zip_path.unlink()
                print(f"  已刪除：{zip_name}")

    def _extract_nested_zip_preserve_structure(
        self, zip_path: Path, extract_dir: Path
    ) -> None:
        """解壓縮巢狀 ZIP，保留其內部目錄結構（不清除目標目錄）"""
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                # 修正檔名編碼：CP437 → Big5
                try:
                    filename_bytes = info.filename.encode('cp437')
                    correct_filename = filename_bytes.decode('big5')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    correct_filename = info.filename

                target_path = extract_dir / correct_filename

                if info.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info) as src, open(target_path, 'wb') as dst:
                        dst.write(src.read())

        print(f"  已解壓縮至：{extract_dir}/")

    def _load_metadata(self) -> Dict:
        """載入現有元資料"""
        if self.config.metadata_path.exists():
            with open(self.config.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'sync_history': []}

    def _update_metadata(self, metadata: Dict, downloaded_files: Dict) -> None:
        """更新元資料檔案"""
        # 從 release.txt 取得版本號
        release_version = self._parse_release_version()

        # 取得 API 修改日期
        api_modified_date = os.getenv('API_MODIFIED_DATE', '')

        # 記錄歷史
        history_entry = {
            'date': datetime.now(timezone.utc).isoformat(),
            'previous_version': metadata.get('release_version', ''),
            'new_version': release_version,
            'changed_files': list(downloaded_files.keys())
        }

        metadata.update({
            'last_sync': datetime.now(timezone.utc).isoformat(),
            'api_modified_date': api_modified_date,
            'release_version': release_version,
            'files': downloaded_files
        })

        # 保留最近 10 筆歷史
        metadata['sync_history'] = (
            [history_entry] + metadata.get('sync_history', [])
        )[:10]

        # 寫入檔案
        with open(self.config.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"元資料已更新：{self.config.metadata_path}")

    def _parse_release_version(self) -> str:
        """從 release.txt 解析版本號"""
        release_path = self.config.data_path / 'release.txt'
        if not release_path.exists():
            return ''

        # 使用 utf-8-sig 處理 BOM
        with open(release_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if '版本：' in line or '版本:' in line:
                    parts = line.split('：') if '：' in line else line.split(':')
                    if len(parts) >= 2:
                        return parts[1].strip()
        return ''

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化檔案大小"""
        size_float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        return f"{size_float:.1f} TB"


def main() -> int:
    syncer = CNS11643Syncer()
    success = syncer.sync()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
