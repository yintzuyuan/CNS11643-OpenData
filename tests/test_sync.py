#!/usr/bin/env python3
"""
CNS11643 資料同步功能測試
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# 將 scripts 目錄加入 path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestSyncConfig(unittest.TestCase):
    """測試同步設定模組"""

    def test_default_api_url(self):
        """測試預設 API URL"""
        from config import SyncConfig

        config = SyncConfig()
        self.assertEqual(
            config.data_gov_api_url, "https://data.gov.tw/api/v2/rest/dataset/5961"
        )

    def test_default_base_url(self):
        """測試預設下載 URL"""
        from config import SyncConfig

        config = SyncConfig()
        self.assertEqual(
            config.cns11643_base_url, "https://www.cns11643.gov.tw/opendata"
        )

    def test_env_override(self):
        """測試環境變數覆蓋預設值"""
        with patch.dict(
            os.environ,
            {
                "DATA_GOV_API_URL": "https://custom.api.url",
                "CNS11643_BASE_URL": "https://custom.base.url",
            },
        ):
            # 重新載入模組以套用新環境變數
            import importlib

            import config

            importlib.reload(config)

            cfg = config.SyncConfig()
            self.assertEqual(cfg.data_gov_api_url, "https://custom.api.url")
            self.assertEqual(cfg.cns11643_base_url, "https://custom.base.url")

    def test_sync_files_list(self):
        """測試同步檔案清單"""
        from config import SyncConfig

        config = SyncConfig()

        # 必須包含的檔案
        required_files = [
            "release.txt",
            "OpenDataFilesList.csv",
            "MapingTables.zip",
            "Properties.zip",
        ]

        for f in required_files:
            self.assertIn(f, config.sync_files)

    def test_metadata_path(self):
        """測試元資料路徑屬性"""
        from config import SyncConfig

        config = SyncConfig()

        expected = config.data_path / config.metadata_file
        self.assertEqual(config.metadata_path, expected)


class TestCheckUpdate(unittest.TestCase):
    """測試更新檢查模組"""

    @patch("check_update.requests.get")
    def test_get_api_modified_date(self, mock_get):
        """測試從 API 取得修改日期"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {"modifiedDate": "2025-11-12 21:55:40"}
        }
        mock_get.return_value = mock_response

        from check_update import get_api_modified_date
        from config import SyncConfig

        result = get_api_modified_date(SyncConfig())
        self.assertEqual(result, "2025-11-12 21:55:40")

    @patch("check_update.requests.get")
    def test_get_remote_release_version(self, mock_get):
        """測試從遠端取得版本號"""
        mock_response = MagicMock()
        mock_response.content = "版本：20250718\n更新日期：2025-07-18".encode(
            "utf-8-sig"
        )
        mock_get.return_value = mock_response

        from check_update import get_remote_release_version
        from config import SyncConfig

        result = get_remote_release_version(SyncConfig())
        self.assertEqual(result, "20250718")

    def test_get_current_metadata_empty(self):
        """測試讀取不存在的元資料"""
        from check_update import get_current_metadata
        from config import SyncConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config = SyncConfig()
            config.root_path = Path(tmpdir)

            result = get_current_metadata(config)
            self.assertEqual(result, {})

    def test_get_current_metadata_exists(self):
        """測試讀取存在的元資料"""
        from check_update import get_current_metadata
        from config import SyncConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config = SyncConfig()
            config.root_path = Path(tmpdir)

            # 建立測試元資料
            metadata = {
                "release_version": "20250325",
                "api_modified_date": "2025-03-25 10:00:00",
            }
            metadata_path = Path(tmpdir) / config.metadata_file
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f)

            result = get_current_metadata(config)
            self.assertEqual(result["release_version"], "20250325")


class TestVerifyData(unittest.TestCase):
    """測試資料驗證模組"""

    def _create_complete_data_structure(self, tmppath: Path) -> None:
        """建立完整的資料結構供測試使用"""
        tables_path = tmppath / "Tables"
        tables_path.mkdir()

        # L1：建立必要目錄結構
        (tables_path / "MapingTables").mkdir()
        (tables_path / "MapingTables" / "Big5").mkdir()
        (tables_path / "MapingTables" / "Unicode").mkdir()
        (tables_path / "MapingTables" / "地政").mkdir()
        (tables_path / "Properties").mkdir()
        (tables_path / "Properties" / "parts").mkdir()

        # L2：建立關鍵檔案
        # 基本資訊
        (tmppath / "release.txt").write_text("版本：20250718", encoding="utf-8")
        (tmppath / "OpenDataFilesList.csv").write_text("test", encoding="utf-8")

        # Big5 對照表
        (tables_path / "MapingTables" / "Big5" / "CNS2BIG5.txt").write_text(
            "test", encoding="utf-8"
        )

        # Unicode 對照表
        (
            tables_path / "MapingTables" / "Unicode" / "CNS2UNICODE_Unicode BMP.txt"
        ).write_text("test", encoding="utf-8")

        # 其他對照表
        for filename in ["CNS2DCI.txt", "CNS2TAX.txt", "CNS2INC.txt", "CNS2FIN.txt"]:
            (tables_path / "MapingTables" / filename).write_text(
                "test", encoding="utf-8"
            )

        # 屬性資料
        for filename in [
            "CNS_phonetic.txt",
            "CNS_radical.txt",
            "CNS_stroke.txt",
            "CNS_cangjie.txt",
        ]:
            (tables_path / "Properties" / filename).write_text("test", encoding="utf-8")

        # parts 目錄需要有檔案
        (tables_path / "Properties" / "parts" / "test.png").write_bytes(b"test")

        # 地政目錄需要有檔案
        (tables_path / "MapingTables" / "地政" / "台北市.txt").write_text(
            "test", encoding="utf-8"
        )

    def test_verify_missing_directory(self):
        """測試缺少目錄時驗證失敗"""
        from verify_data import verify_directories

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            errors = verify_directories(tmppath)
            self.assertTrue(len(errors) > 0)
            self.assertTrue(any("Tables/MapingTables" in e for e in errors))

    def test_verify_missing_files(self):
        """測試缺少檔案時驗證失敗"""
        from verify_data import verify_files

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            errors = verify_files(tmppath)
            self.assertTrue(len(errors) > 0)
            self.assertTrue(any("release.txt" in e for e in errors))

    def test_verify_complete_data(self):
        """測試完整資料時驗證成功"""
        from config import SyncConfig
        from verify_data import verify_data

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            self._create_complete_data_structure(tmppath)

            # 建立元資料
            metadata = {"release_version": "20250718"}
            with open(tmppath / "sync_metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f)

            config = SyncConfig()
            config.root_path = tmppath
            config.tables_path = tmppath / "Tables"

            result = verify_data(config)
            self.assertTrue(result)

    def test_verify_skip_metadata(self):
        """測試跳過元資料驗證"""
        from config import SyncConfig
        from verify_data import verify_data

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            self._create_complete_data_structure(tmppath)

            # 不建立元資料，但使用 skip_metadata=True
            config = SyncConfig()
            config.root_path = tmppath
            config.tables_path = tmppath / "Tables"

            result = verify_data(config, skip_metadata=True)
            self.assertTrue(result)


class TestSyncCNS11643(unittest.TestCase):
    """測試同步模組"""

    def test_format_size(self):
        """測試檔案大小格式化"""
        from sync_cns11643 import CNS11643Syncer

        self.assertEqual(CNS11643Syncer._format_size(1024), "1.0 KB")
        self.assertEqual(CNS11643Syncer._format_size(1048576), "1.0 MB")
        self.assertEqual(CNS11643Syncer._format_size(500), "500.0 B")

    def test_parse_release_version(self):
        """測試解析版本號"""
        from config import SyncConfig
        from sync_cns11643 import CNS11643Syncer

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # 建立 release.txt
            (tmppath / "release.txt").write_text(
                "版本：20250718\n更新日期：2025-07-18", encoding="utf-8"
            )

            config = SyncConfig()
            config.root_path = tmppath

            syncer = CNS11643Syncer(config)
            result = syncer._parse_release_version()
            self.assertEqual(result, "20250718")

    def test_extract_nested_zips(self):
        """測試巢狀 ZIP 檔案解壓縮（保留 ZIP 內部目錄結構）"""
        import zipfile

        from config import SyncConfig
        from sync_cns11643 import CNS11643Syncer

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            properties_dir = tmppath / "Properties"
            properties_dir.mkdir()

            # 建立模擬的 CNS_component_word.zip
            # ZIP 內部已有 parts/ 目錄結構（與實際檔案結構相同）
            nested_zip_path = properties_dir / "CNS_component_word.zip"
            with zipfile.ZipFile(nested_zip_path, "w") as zf:
                zf.writestr("parts/test_part.png", b"fake png data")
                zf.writestr("parts/subdir/another.png", b"more data")

            config = SyncConfig()
            config.tables_path = tmppath

            syncer = CNS11643Syncer(config)
            syncer._extract_nested_zips(properties_dir)

            # 驗證解壓縮結果（ZIP 內的 parts/ 目錄被保留）
            parts_dir = properties_dir / "parts"
            self.assertTrue(parts_dir.is_dir())
            self.assertTrue((parts_dir / "test_part.png").exists())
            self.assertTrue((parts_dir / "subdir" / "another.png").exists())

            # 驗證巢狀 ZIP 已被刪除
            self.assertFalse(nested_zip_path.exists())


if __name__ == "__main__":
    unittest.main()
