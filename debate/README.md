# 《左傳》真偽辯論：劉歆偽造說 vs. 先秦成書說

三個 Claude Code 子代理（subagents）＋一份辯論協議，用網路上的學術資源，就
**「今本《春秋左氏傳》係西漢末劉歆偽造」** 這一命題進行五回合辯論，最後由仲裁者裁決。

本目錄目前是「設計稿」狀態：三個 agent 的 system prompt、辯論協議、評分規準、
種子書目都已寫好，**尚未執行任何一回合**。請先審閱，確認後再啟動。

## 檔案地圖

| 檔案 | 內容 | 審閱重點 |
| --- | --- | --- |
| `debate/PROTOCOL.md` | 命題定義（強／弱命題）、五回合結構、引證規範、證據分級、禁手、輸出格式、仲裁規準 | 規則是否夠嚴、是否公平 |
| `.claude/agents/zuozhuan-pro-forgery.md` | **正方**：主張劉歆偽造／改編（劉逢祿→康有為→崔適→徐仁甫→津田左右吉一脈） | 是否能把少數派論點推到最強而不造假 |
| `.claude/agents/zuozhuan-anti-forgery.md` | **反方**：主張先秦成書（錢穆、Karlgren、新城新藏、楊伯峻、出土文獻一脈） | 是否會偷懶訴諸「學界共識」而不舉證 |
| `.claude/agents/zuozhuan-arbitrator.md` | **仲裁者**：抽查引文真偽、依規準計分、對強／弱命題分別裁決 | 抽查與扣分機制是否足以嚇阻捏造 |
| `.claude/skills/zuozhuan-debate/SKILL.md` | 主控流程：如何依序喚起三個 agent、傳遞回合檔、產生裁決 | 流程是否可重現 |
| `debate/bibliography/seed.md` | 種子書目（雙方各自的核心文獻，附核實狀態） | 有無漏掉關鍵文獻、有無錯誤 |
| `debate/templates/round.md`、`verdict.md` | 回合稿與裁決書的固定格式 | 格式是否便於事後查核 |
| `debate/transcript/` | 執行後的逐回合稿與裁決書（目前為空） | — |

## 設計原則

1. **一切論述必有出處。** 每一條事實性主張都要對應「引文表」中的一筆，並標示證據等級
   `[A]` 已讀全文／`[B]` 僅由檢索結果確認存在與大意／`[C]` 背景知識、本次未能線上核實。
   `[C]` 不得作為關鍵論點的唯一支撐；捏造出處由仲裁者重罰。
2. **命題要精確。** 「劉歆偽造」在學術史上有強弱兩版（康有為 vs. 劉逢祿），
   正方第一回合必須宣告自己守哪一版；仲裁者對兩版分別裁決，避免「打贏弱版、宣稱強版」。
3. **交鋒有義務。** 第二回合起，未回應對方編號論點者視同讓步，由仲裁者記錄。
4. **少數派也要被認真對待。** 正方的任務是把偽造說做成最強版本（steelman），
   反方不得以「學界早有定論」代替舉證；仲裁者依證據而非依人數裁決，但「共識」本身
   可作為一項有理由的證據被權衡。
5. **不可否證的招式要被點名。** 例如以「《漢書》亦劉歆所竄」消解一切漢代證據，
   仲裁者須明確標記為循環／不可否證論證並扣分。

## 執行方式（審閱通過後）

在 Claude Code 中輸入：

```
/zuozhuan-debate
```

主控流程會：喚起正方寫 R1 → 反方寫 R1 → 正方 R2（讀反方 R1）→ … → R5 →
喚起仲裁者讀全部十篇回合稿、抽查引文、寫 `debate/transcript/verdict.md`。
每個 agent 直接把回合稿寫入 `debate/transcript/`，主 session 只負責排程與傳遞檔名。

也可以只跑單一 agent 做「模擬考」：例如
「請用 zuozhuan-pro-forgery agent 寫一篇 R1 立論，只寫檔不進入後續回合」。

## 環境限制（重要）

本 session 執行於 Claude Code on the web 的受管容器，網路政策只放行 WebSearch
（回傳標題、URL 與摘要片段），對 ctext.org、zh.wikisource.org、archive.org、
cambridge.org、jstor.org、hkbu.edu.hk、tsinghua.edu.cn 等學術站台的 WebFetch
全文讀取皆被 egress proxy 拒絕（已實測，見 PROTOCOL 附錄）。

後果：在此環境中，多數引文最多只能達到 `[B]` 等級，仲裁者也只能用檢索結果做抽查。
若要讓引文達到 `[A]`（讀到原文），請在網路政策較寬鬆的環境中執行，或在本機以
`claude` CLI 執行本流程。協議已包含「WebFetch 被擋時的降級規則」，
兩種環境都能跑，只是可核實深度不同。

參考：<https://code.claude.com/docs/en/claude-code-on-the-web>（環境與網路政策說明）。

## 本地文獻（可讓引文達到 [A] 級，不受網路限制）

把掃描 PDF 放進 `debate/bibliography/local/`，agent 就能用 Read 逐頁核對、給頁碼引用。
目前設計以《古史辨》第五冊為第一優先（使用者 Drive 已有全本掃描，但無文字層）。

把檔案送進容器的可行途徑（本環境 Drive 連接器只能讀文字，不能搬 24 MB 二進位檔；drive.google.com 亦被擋）：
1. **推到本分支**：`git checkout claude/zuozhuan-authenticity-debate-w2tz8f`，把 PDF 複製為
   `debate/bibliography/local/gushibian-5.pdf`，commit 並 push。GitHub 單檔上限 100 MB；網頁拖曳上傳上限 25 MB（第五冊 24.4 MB 剛好可以）。
2. 之後在 session 中 `git pull`，再跑 OCR 產生可 grep 的定位文字：
   ```
   pip install pymupdf rapidocr-onnxruntime
   python3 debate/tools/ocr_pdf.py debate/bibliography/local/gushibian-5.pdf
   ```
   輸出 `gushibian-5.txt`，每頁以 `==== page N ====` 分隔（N 為 PDF 物理頁）。OCR 只用來定位，引文須回到頁面影像核對。

`debate/bibliography/seed.md` 一之二節已依 1935 年《古史辨總目》整理出第五冊全部篇目與起頁。

## 語言

回合稿與裁決書一律用繁體中文撰寫；書名、篇名、人名保留原文（中、日、英）。
