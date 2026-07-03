# Foodtopia Backend

Foodtopia 網頁版 MVP 後端，使用 FastAPI 建立。

## 目標流程

第一階段先跑通：

```text
商家註冊 -> 商家登入 -> 建立福袋 -> 使用者瀏覽福袋 -> 使用者預約 -> 商家確認取貨
```

## 專案結構

```text
backend/
  app/
    main.py
    db.py
    models.py
    schemas.py
    auth.py
    routers/
      merchant_auth.py
      surprise_bags.py
      reservations.py
  requirements.txt
```

## 預計 API

```text
POST  /merchant-auth/register
POST  /merchant-auth/login
POST  /merchant/surprise-bags
GET   /surprise-bags
POST  /reservations
GET   /merchant/reservations
PATCH /merchant/reservations/{reservation_id}/picked-up
```

## 開發啟動方式

之後安裝依賴後可用：

```bash
uvicorn app.main:app --reload
```
