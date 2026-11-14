# Dragon City Battle Timer - Cloud Server

Server đám mây hẹn giờ làm nhiệm vụ **Đánh rồng Battle (Heroic Race)** trong game Dragon City.
Chạy trên nền tảng **FastAPI**, lưu trữ trạng thái đếm ngược và tự động bắn **Discord Webhook kèm chuông & rung** về điện thoại khi hết giờ (kể cả khi bạn đã tắt máy tính).

---

## Tính Năng Chính
- **Đếm ngược thời gian thực:** Đồng hồ đếm ngược giao diện Web Dashboard trực quan hiển thị trên cả điện thoại và máy tính (`GET /`).
- **Chuẩn múi giờ Việt Nam:** Tích hợp `Asia/Ho_Chi_Minh` (UTC+7), không bị lệch giờ server quốc tế.
- **Tương thích Render Free Tier:**
  - Siêu nhẹ (<40MB RAM, chuẩn 512MB RAM miễn phí của Render).
  - Endpoint `GET /api/cron` kết hợp với **cron-job.org** ping đánh thức server định kỳ 1–2 phút.
- **Lưu trữ bền vững:** Tự động lưu `timers_cloud.json` để không mất lịch hẹn khi container Render khởi động lại.
- **Discord Alert:** Bắn thông báo kèm tag `@everyone` để điện thoại đổ chuông và rung thông báo lập tức.

---

## Cấu Trúc Thư Mục
```
├── server.py           # Mã nguồn chính FastAPI server & Web dashboard
├── requirements.txt    # Danh sách thư viện Python cần cài đặt
├── Procfile            # Lệnh khởi chạy server trên Render
├── render.yaml         # Cấu hình Render Blueprint deploy 1-click
├── README_RENDER.md    # Hướng dẫn chi tiết triển khai lên Render & cron-job.org
└── .gitignore
```

---

## Triển Khai Lên Render
1. Tạo Web Service mới trên [Render.com](https://render.com).
2. Kết nối với repository GitHub này.
3. Cài đặt các thông số:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     - `DISCORD_WEBHOOK`: `https://discord.com/api/webhooks/...`
     - `SECRET_KEY`: `dragoncity_battle_2026`
4. Lấy URL Render được cấp và cài đặt lịch ping 1-2 phút trên [cron-job.org](https://cron-job.org) trỏ vào `/api/cron`.
