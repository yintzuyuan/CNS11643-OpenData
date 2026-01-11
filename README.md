# CNS11643 全字庫開放資料 - 對照表與屬性資料

## 簡介
本儲存庫包含台灣CNS11643全字庫開放資料中的對照表與屬性資料。CNS11643是台灣的國家標準交換碼，這些資料對中文資訊處理和研究極為有用。

## 資料來源
資料來自台灣政府的公開資料平台，最後更新日期請參考 `release.txt` 文件。

## 注意事項
本儲存庫僅包含對照表與屬性資料。原始資料集還包含字型檔案（楷體和宋體）以及中文字音檔。如需完整資料集，請訪問[CNS11643全字庫官方網站](https://www.cns11643.gov.tw/)或[台灣政府開放資料平台](https://data.gov.tw/)下載。

## 儲存庫結構
- `Tables/`: 對照表與屬性資料
  - `MapingTables/`: 各種編碼對照表
    - `Big5/`: CNS對Big5相關編碼的對照表
    - `Unicode/`: CNS對Unicode各字面的對照表
    - `地政/`: 25個縣市的地政系統對照表（縣市未合併及升格前）
    - `CNS2DCI.txt`: CNS 對公路監理電信內碼對照表
    - `CNS2FIN.txt`: CNS 對稅務內碼對照表
    - `CNS2INC.txt`: CNS 對工商內碼對照表
    - `CNS2TAX.txt`: CNS 對財稅交換碼對照表
    - `全字庫中文對照表說明文件.txt`: 對照表格式說明
  - `Properties/`: 字符屬性資料
    - `parts/`: 全字庫部件圖檔 (由 `CNS_component_word.zip` 解壓縮)
    - `CNS_phonetic.txt`: 注音資料
    - `CNS_cangjie.txt`: 倉頡碼資料
    - `CNS_stroke.txt`: 筆畫數資料
    - `CNS_radical.txt`: 部首代號資料
    - `CNS_radical_word.txt`: 部首代號對應字碼表
    - `CNS_pinyin_1.txt`: 拼音資料 (調值表示)
    - `CNS_pinyin_2.txt`: 拼音資料 (聲調符號表示)
    - `CNS_component.txt`: 部件代號資料
    - `CNS_component_word.txt`: 部件代號說明表
    - `CNS_strokes_sequence.txt`: 筆順資料
    - `CNS_source.txt`: 字形來源資料
    - `全字庫屬性資料說明文件.txt`: 屬性資料格式說明
- `OpenDataFilesList.csv`: 原始開放資料包中的檔案清單。
- `release.txt`: 發布說明和更新日誌。
- `README.md`: 本說明文件。

## 主要檔案說明

### 根目錄檔案
- `OpenDataFilesList.csv`: 列出從政府開放資料平台下載的原始壓縮檔內包含的所有檔案名稱。
- `release.txt`: 包含資料集的版本資訊、發布日期和可能的更新內容摘要。

### 對照表 (`Tables/MapingTables/`)
- `Big5/`: 包含 CNS 對 Big5、Big5E、倚天外字集、Big5符號及控制字元的對照表。
- `Unicode/`: 包含 CNS 對 Unicode BMP (第0字面)、第2字面、第15字面的對照表。
- `地政/`: 包含基隆市、台北市、台北縣...等25個縣市的地政用字對照表。
- `CNS2DCI.txt`, `CNS2FIN.txt`, `CNS2INC.txt`, `CNS2TAX.txt`: 分別為 CNS 對公路監理、稅務、工商、財稅領域特定內碼的對照表。
- `全字庫中文對照表說明文件.txt`: 詳細說明各對照表的欄位格式與意義。

### 屬性資料 (`Tables/Properties/`)
- `CNS_phonetic.txt`: 提供 CNS 字碼對應的注音符號。
- `CNS_cangjie.txt`: 提供 CNS 字碼對應的倉頡碼。
- `CNS_stroke.txt`: 提供 CNS 字碼對應的總筆畫數。
- `CNS_radical.txt` & `CNS_radical_word.txt`: 提供 CNS 字碼的部首資訊（需互相對照使用）。
- `CNS_pinyin_1.txt` & `CNS_pinyin_2.txt`: 提供注音到不同拼音系統（漢語、注音二式、耶魯、韋式、通用）的對照，分別使用調值和聲調符號表示。
- `CNS_component.txt` & `CNS_component_word.txt`: 提供 CNS 字碼的部件拆解資訊（需互相對照使用）。
- `CNS_strokes_sequence.txt`: 提供 CNS 字碼的筆順序列（以數字1-5代表橫、豎、撇、點、折）。
- `CNS_source.txt`: 提供 CNS 字碼的來源資訊。
- `全字庫屬性資料說明文件.txt`: 詳細說明各屬性資料表的欄位格式與意義。

## 使用說明
1. clone 或下載本儲存庫。
2. 根據需求選用 `Tables/` 目錄下的對照表或屬性資料。
3. **強烈建議在使用前先閱讀各資料夾內的說明文件 (`全字庫*.txt`) 以了解詳細的資料格式。**

## 授權資訊
使用本資料時，請遵守台灣政府對開放資料的使用規範。相關規範請參考政府資料開放平臺。

## 更新資訊

本儲存庫透過 GitHub Actions 每週自動檢查 CNS11643 資料更新，並建立 PR 供審核。

### 自動同步範圍

| 資料 | 說明 |
|------|------|
| MapingTables | Unicode、Big5 編碼映射表 |
| Properties | 注音、拼音、部首、筆畫等屬性資料 |

### 手動下載（大型檔案）

以下檔案超過 GitHub 100MB 限制，需從官網下載：

| 檔案 | 下載連結 |
|------|----------|
| 宋體字型 | https://www.cns11643.gov.tw/opendata/Fonts_Sung.zip |
| 楷體字型 | https://www.cns11643.gov.tw/opendata/Fonts_Kai.zip |
| 聲音檔案 | https://www.cns11643.gov.tw/opendata/Voice.zip |

下載後解壓縮至 `data/CNS11643/` 目錄。

## 相關連結
- [CNS11643全字庫官方網站](https://www.cns11643.gov.tw/)
- [台灣政府開放資料平台](https://data.gov.tw/)
