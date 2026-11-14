# HƯỚNG DẪN TRIỂN KHAI CLOUD WEB APP LÊN RENDER & CRON-JOB.ORG

Hệ thống cho phép bạn hẹn giờ đếm ngược nhiệm vụ **Đánh rồng Battle (Heroic Race)** hoàn toàn trên đám mây. Khi hết giờ, server sẽ tự động bắn tin nhắn **Discord Webhook kèm chuông và rung** trực tiếp về điện thoại của bạn, ngay cả khi tắt máy tính!

---

## BƯỚC 1: TRIỂN KHAI LÊN RENDER (HOÀN TOÀN MIỄN PHÍ)

1. Đăng ký/Đăng nhập tài khoản miễn phí tại [Render.com](https://render.com).
2. Tạo một Repository mới trên GitHub (hoặc tải thư mục `web_timer/` lên GitHub cá nhân).
3. Tại trang chủ Render Dashboard:
   - Bấm **New +** -> Chọn **Web Service**.
   - Kết nối với GitHub Repository chứa mã nguồn `web_timer/`.
4. Điền các thông số:
   - **Name:** `dragon-city-timer` (hoặc tên tùy thích).
   - **Region:** `Singapore` (để độ trễ về Việt Nam thấp nhất).
   - **Runtime:** `Python 3`.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Chọn **Free** (Miễn phí).
5. Thêm biến môi trường (**Environment Variables**):
   - `DISCORD_WEBHOOK`: `https://discord.com/api/webhooks/1571126372599070780/JoLO7Qn-hn2mXCIle7x72-7WsBei3M3z5_S9WfI5TdOe_GV3rTczTqSfmNuF-4qMjfLZ`
   - `SECRET_KEY`: `dragoncity_battle_2026`
6. Bấm **Create Web Service**. Chờ 1-2 phút, Render sẽ cấp cho bạn một đường dẫn URL:
   `https://dragon-city-timer.onrender.com`

---

## BƯỚC 2: CẤU HÌNH CRON-JOB.ORG ĐỂ ĐÁNH THỨC & BẮN THÔNG BÁO

Vì gói Free của Render sẽ ngủ đông sau 15 phút, chúng ta dùng dịch vụ miễn phí **cron-job.org** để ping đánh thức và kiểm tra hết giờ:

1. Đăng ký tài khoản tại [cron-job.org](https://cron-job.org).
2. Bấm **Create Cronjob**:
   - **Title:** `Dragon City Timer Ping`
   - **URL:** `https://dragon-city-timer.onrender.com/api/cron`
   - **Execution Schedule:** Chọn **Every 1 minute** hoặc **Every 2 minutes** (mỗi 1 đến 2 phút).
3. Bấm **Create**.
4. Xong! Cứ mỗi 1-2 phút, cron-job sẽ gọi vào server. Nếu đến giờ hồi Battle Dragon, server Render sẽ lập tức gửi Discord Webhook làm rung điện thoại bạn!

---

## BƯỚC 3: KẾT NỐI VỚI DRAGON CITY BOT TRÊN MÁY TÍNH

1. Mở app **Dragon City Bot Pro** trên PC.
2. Bấm vào nút **⏱️ Hẹn Giờ Battle** (hoặc mở tool `Hẹn Giờ Battle (Đánh Rồng)`).
3. Tại mục **Cloud Web App URL (Render - Tùy chọn)**:
   - Dán URL của bạn: `https://dragon-city-timer.onrender.com`
4. Mỗi khi bạn dùng phím tắt **`Ctrl + Shift + T`** để quét thời gian chờ:
   - Máy tính đếm ngược real-time chính xác từng giây.
   - Đồng thời tự động đẩy lịch hẹn lên Cloud Render.
   - Dù bạn có tắt máy tính, server Render + cron-job.org vẫn hoạt động và báo chuông rung về điện thoại đúng giờ!
