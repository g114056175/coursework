# coursework

研究所課程作業與成果，依課程分類。每份作業的說明與原始資料保留在對應子資料夾。

| 課程 | 內容 |
| --- | --- |
| [AIOT](AIOT/) | [HW3](AIOT/hw3/)、[HW4](AIOT/hw4/)、[HW5](AIOT/hw5/)、[HW6](AIOT/hw6/) |
| [DRL／深度強化學習](DRL/) | [DIC1](DRL/DIC1/)、[HW1](DRL/hw1/)、[HW2](DRL/hw2/)、[HW3](DRL/hw3/)、[期末成果](DRL/final-project/) |
| [IR／資料檢索](IR/) | [school_data](IR/school_data/)：IR_HW5 的 JSON 資料 |
| [DSDP／資料結構與資料處理](DSDP/) | [Data_Models_And_Processing](DSDP/Data_Models_And_Processing/)：時空人流預測 |

## 執行與展示

各作業使用的 Python 套件、資料來源、模型及服務設定不同，請依子資料夾 README 操作。期末簡報、影片、模型與資料仍保留原有內容。

網頁展示入口見 [課程展示頁](https://g114056175.github.io/coursework/)。原有倉庫與展示網址目前保留，供搬遷後人工核對。

DRL HW1 的 Hugging Face 同步已調整為手動工作流程；在新倉庫設定 `HF_TOKEN` secret 後，從 Actions 執行「DRL HW1 - Sync to Hugging Face」。本次搬遷不會更新既有 Hugging Face Space。

<details>
<summary>搬遷與新增作業</summary>

2026-10-04 從 11 個課程倉庫整合，保留來源分支提交紀錄。來源分支與標籤快照位於 `source/<原倉庫>/branches/…`、`source/<原倉庫>/tags/…` 標籤下；來源提交與檔案樹比對見 [migration.json](migration.json)。

新增作業時，在課程資料夾下建立作業目錄，附上 README、依賴及必要資料來源說明，再更新本頁索引。

```powershell
git clone https://github.com/g114056175/coursework.git
cd coursework
# 放入新的作業，例如 IR/hw6/
git add -- IR/hw6/ README.md
git commit -m "Add IR homework 6"
git push origin main
```

各子專案的授權檔案沿用原內容，不另行覆蓋。

</details>
