# Alpha ngrok 測試流程

這份流程是給遠端 alpha 商家短期測試用。你的 Mac 必須保持開機，四個 terminal 都不能關。

## 1. 啟動後端

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 2. 開後端 ngrok

```bash
ngrok http 8080
```

記下後端網址，例如：

```text
https://abc123.ngrok-free.app
```

## 3. 啟動前端

把 `VITE_API_BASE_URL` 換成你的後端 ngrok 網址：

```bash
cd frontend
VITE_API_BASE_URL=https://abc123.ngrok-free.app npm run dev:public
```

## 4. 開前端 ngrok

看前端 terminal 顯示的 port，通常是 `5173`，如果被占用可能會變 `5174`。

```bash
ngrok http 5173
```

如果 Vite 顯示 `http://127.0.0.1:5174/`，就改成：

```bash
ngrok http 5174
```

把這個前端 ngrok 網址給商家測試。

## 注意事項

- 前端 ngrok 網址是給商家打開的網址。
- 後端 ngrok 網址只填在 `VITE_API_BASE_URL`，通常不用給商家。
- 如果重開 ngrok，免費網址可能會變，前端也要重啟並填新的 `VITE_API_BASE_URL`。
- 如果頁面顯示 `Blocked request. This host ... is not allowed.`，請確認 `frontend/vite.config.ts` 有允許 `.ngrok-free.app`，並重啟前端 dev server。
- 這是臨時 alpha 測試方式，不適合長期正式營運。
