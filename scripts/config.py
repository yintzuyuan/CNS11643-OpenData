#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNS11643 同步設定檔
所有設定皆透過環境變數配置，避免硬編碼
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class SyncConfig:
    """同步設定"""

    # API 端點
    data_gov_api_url: str = field(
        default_factory=lambda: os.getenv(
            'DATA_GOV_API_URL',
            'https://data.gov.tw/api/v2/rest/dataset/5961'
        )
    )

    # 下載基礎 URL
    cns11643_base_url: str = field(
        default_factory=lambda: os.getenv(
            'CNS11643_BASE_URL',
            'https://www.cns11643.gov.tw/opendata'
        )
    )

    # 根目錄（release.txt, OpenDataFilesList.csv 存放位置）
    root_path: Path = field(
        default_factory=lambda: Path(
            os.getenv('PROJECT_ROOT', '.')
        )
    )

    # 對照表目錄（MapingTables, Properties 解壓縮位置）
    tables_path: Path = field(
        default_factory=lambda: Path(
            os.getenv('TABLES_PATH', './Tables')
        )
    )

    # 相容性：data_path 指向根目錄
    @property
    def data_path(self) -> Path:
        return self.root_path

    # 元資料檔案名稱
    metadata_file: str = 'sync_metadata.json'

    # 強制下載
    force_download: bool = field(
        default_factory=lambda: os.getenv('FORCE_DOWNLOAD', 'false').lower() == 'true'
    )

    # 下載超時設定（秒）
    download_timeout: int = field(
        default_factory=lambda: int(os.getenv('DOWNLOAD_TIMEOUT', '300'))
    )

    # 要同步的檔案清單
    sync_files: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.sync_files:
            self.sync_files = [
                'release.txt',
                'OpenDataFilesList.csv',
                'MapingTables.zip',
                'Properties.zip',
            ]

    @property
    def metadata_path(self) -> Path:
        """元資料檔案完整路徑"""
        return self.data_path / self.metadata_file
