---
name: zuozhuan-debate
description: 主控《左傳》真偽五回合辯論：依序喚起 zuozhuan-pro-forgery、zuozhuan-anti-forgery 寫 R1–R5 回合稿，再喚起 zuozhuan-arbitrator 抽查引文並寫裁決書。用法：/zuozhuan-debate（全程）、/zuozhuan-debate R3（從 R3 續跑）、/zuozhuan-debate exam pro（只讓正方寫 R1 模擬考）。
---

# /zuozhuan-debate — 主控流程

你（主 session）是排程者，不是辯手。你的工作只有：依序喚起 agent、把檔名傳給它們、
在每回合後 commit，最後喚起仲裁者。**不要自己替任一方寫論點，也不要摘要對方稿件餵給 agent**
（agent 自己會 Read 檔案，這樣才不會被你的摘要偏誤影響）。

## 0. 前置檢查

```
ls debate/PROTOCOL.md debate/templates/round.md debate/templates/verdict.md debate/bibliography/seed.md
ls .claude/agents/zuozhuan-pro-forgery.md .claude/agents/zuozhuan-anti-forgery.md .claude/agents/zuozhuan-arbitrator.md
ls debate/transcript/
```

- 若 `debate/transcript/` 已有 R{n} 檔，且使用者未指定回合，先問是要**續跑**還是**清空重跑**（清空前列出將刪除的檔案）。
- 檢查 `debate/bibliography/local/`：若有 `*.pdf` 而無同名 `*.txt`，先跑
  `python3 debate/tools/ocr_pdf.py <pdf>`（背景執行，數百頁約需十幾分鐘），再啟動辯論；
  啟動訊息中列出可用的本地文獻，提醒 agent 依 seed.md 規則以 Read 核頁後標 [A]。
- 用 WebFetch 試打一次 `https://ctext.org/chun-qiu-zuo-zhuan/zh`。若回 EGRESS_BLOCKED，在啟動訊息中告知使用者：本環境引文上限實務上是 [B]。

## 1. 參數

| 呼叫方式 | 行為 |
| --- | --- |
| `/zuozhuan-debate` | R1→R5 全程＋仲裁 |
| `/zuozhuan-debate R{n}` | 從 R{n} 正方開始續跑（需 R1…R{n−1} 十篇中的對應檔已存在） |
| `/zuozhuan-debate exam pro`／`exam con` | 只喚起一方寫 R1，寫完即停，不進入後續回合、不仲裁 |
| `/zuozhuan-debate verdict` | 十篇齊全時只跑仲裁 |

## 2. 回合迴圈（n = 1…5）

每回合兩步，**嚴格串行**（反方必須讀到正方本回合稿）：

### 2a. 正方

第一次喚起用 `Agent`（`subagent_type: "zuozhuan-pro-forgery"`, `run_in_background: false`），
之後各回合用 `SendMessage` 送到同一個 agent，讓它保有前幾回合的查證脈絡。
若該 agent 已不存在，重新 `Agent` 喚起即可（它會自己 Read 既有稿件）。

訊息內容（照抄，只換 n 與主題）：

```
現在是第 {n} 回合。主題：{PROTOCOL §2 該回合主題一行}。
請依 debate/PROTOCOL.md 與 debate/templates/round.md 寫正方稿，
寫入 debate/transcript/R{n}-pro.md。
{n≥2 時加：反方上一回合稿在 debate/transcript/R{n-1}-con.md，請先讀。}
回傳三行即可：檔名、論點編號清單、[A]/[B]/[C] 筆數。
```

### 2b. 反方

同上，`subagent_type: "zuozhuan-anti-forgery"`，寫入 `debate/transcript/R{n}-con.md`，
訊息中指明「正方本回合稿在 debate/transcript/R{n}-pro.md，請先讀」。

### 2c. 回合結束

```
git add debate/transcript/R{n}-pro.md debate/transcript/R{n}-con.md
git commit -m "debate: round {n} (pro/con)"
```

確認兩檔都存在、非空、含「引文表」字樣；否則把缺失回報給對應 agent 重寫，不要自己補。

## 3. 仲裁

十篇齊全後 `Agent`（`subagent_type: "zuozhuan-arbitrator"`, `run_in_background: false`）：

```
五回合十篇稿已齊，在 debate/transcript/。請依 debate/PROTOCOL.md §6 與
debate/templates/verdict.md：先抽查引文寫 citations-check.md，再寫 verdict.md。
回傳五行即可。
```

完成後：

```
git add debate/transcript/citations-check.md debate/transcript/verdict.md
git commit -m "debate: arbitration"
git push -u origin <當前分支>
```

## 4. 對使用者的收尾訊息

只需：裁決（S、W 各一行含信心度）、雙方總分、抽查發現的捏造／誤引筆數、
以及 `debate/transcript/verdict.md` 的路徑。不要重貼裁決書全文。

## 注意

- 每次只跑一個 agent，不要並行正反方。
- 不要在傳遞訊息裡加入你對任一方論點的評價。
- agent 回報引文表全是 [C] 時，提醒它 PROTOCOL §3.2 的限制，請它至少把關鍵論點的支撐升到 [B]，再重寫一次；最多重寫一次。
