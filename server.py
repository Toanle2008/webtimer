"""
Dragon City Cloud Timer Server - FastAPI Web App for Render & Cron-job.org.
Manages countdown timers in the cloud and fires Discord Webhook alerts to phone when expired.
Configured with Vietnam Timezone (Asia/Ho_Chi_Minh).
Auto-saves state to timers_cloud.json for resilience against container restarts.
"""
import os
import json
import time
import threading
import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import pytz

app = FastAPI(title="Dragon City Battle Timer Cloud API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
DEFAULT_DISCORD_WEBHOOK = os.getenv(
    "DISCORD_WEBHOOK", 
    "https://discord.com/api/webhooks/1571126372599070780/JoLO7Qn-hn2mXCIle7x72-7WsBei3M3z5_S9WfI5TdOe_GV3rTczTqSfmNuF-4qMjfLZ"
)
CRON_SECRET_KEY = os.getenv("SECRET_KEY", "dragoncity_secret_2026")
CLOUD_DATA_FILE = os.getenv("CLOUD_DATA_FILE", "timers_cloud.json")

# In-memory storage for cloud timers
timers_db: Dict[str, Dict[str, Any]] = {}


def load_cloud_timers():
    """Đọc timer đã lưu từ file JSON để chống mất dữ liệu khi container khởi động lại."""
    global timers_db
    if os.path.exists(CLOUD_DATA_FILE):
        try:
            with open(CLOUD_DATA_FILE, "r", encoding="utf-8") as f:
                timers_db = json.load(f)
                print(f"[CloudServer] Đã khôi phục dữ liệu từ {CLOUD_DATA_FILE}")
        except Exception as e:
            print(f"[CloudServer] Lỗi đọc {CLOUD_DATA_FILE}: {e}")


def save_cloud_timers():
    """Lưu timer hiện tại vào file JSON trên disk."""
    try:
        with open(CLOUD_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(timers_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CloudServer] Lỗi lưu {CLOUD_DATA_FILE}: {e}")


load_cloud_timers()


class TimerCreateRequest(BaseModel):
    id: Optional[str] = None
    task_name: Optional[str] = "Đánh rồng Battle (Heroic Race)"
    duration_seconds: int
    target_timestamp: Optional[float] = None
    discord_webhook: Optional[str] = None
    ping_everyone: Optional[bool] = True
    secret_key: Optional[str] = None


class WebhookTestRequest(BaseModel):
    webhook_url: Optional[str] = None


def send_discord_alert(timer: Dict[str, Any]) -> bool:
    """Gửi HTTP POST sang Discord Webhook kèm chuông & rung điện thoại."""
    url = timer.get("discord_webhook") or DEFAULT_DISCORD_WEBHOOK
    if not url:
        return False

    now_vn = datetime.datetime.now(VN_TZ).strftime("%H:%M:%S ngày %d/%m/%Y")
    mention = "@everyone " if timer.get("ping_everyone", True) else ""
    task_name = timer.get("task_name", "Đánh rồng Battle")
    duration_str = timer.get("duration_str", "")

    payload = {
        "content": f"{mention}🚨 **[DRAGON CITY - CLOUD ALERT] ĐÃ ĐẾN GIỜ ĐÁNH RỒNG BATTLE!** 🚨",
        "username": "Dragon City Cloud Alert",
        "avatar_url": "https://i.imgur.com/8Q0Zp0V.png",
        "embeds": [
            {
                "title": f"⚔️ {task_name.upper()} ĐÃ HỒI LƯỢT!",
                "description": (
                    "⏰ **Bộ hẹn giờ đám mây đã hoàn tất!**\n"
                    "Hãy mở Dragon City ngay trên điện thoại để đánh trận và đua Heroic Race kịp thời gian!"
                ),
                "color": 15682852,  # Đỏ cam (0xEF4444)
                "fields": [
                    {
                        "name": "⏱️ Thời gian đã chờ",
                        "value": f"**{duration_str}**" if duration_str else "Theo lịch hẹn",
                        "inline": True
                    },
                    {
                        "name": "🔔 Giờ báo thức (VN)",
                        "value": f"**{now_vn}**",
                        "inline": True
                    },
                    {
                        "name": "🌐 Nguồn phát",
                        "value": "Render Cloud + Cron-job.org",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Dragon City Bot Cloud • Heroic Race Timer"
                },
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=8.0)
        return resp.status_code in [200, 204]
    except Exception as e:
        print(f"[CloudServer] Lỗi gửi Discord webhook: {e}")
        return False


def _cloud_background_loop():
    """Luồng nền chạy ngầm bên trong FastAPI kiểm tra từng giây khi server đang thức."""
    while True:
        try:
            active = timers_db.get("active")
            if active and active.get("status") == "running" and not active.get("notified", False):
                now = time.time()
                target = active.get("target_timestamp", 0)
                if now >= target:
                    print(f"[CloudServer] 🚨 Đến giờ hẹn ({active.get('task_name')}), đang gửi Discord...")
                    send_discord_alert(active)
                    active["status"] = "completed"
                    active["notified"] = True
                    save_cloud_timers()
        except Exception as e:
            print(f"[CloudServer] Lỗi background loop: {e}")
        time.sleep(1.0)


# Khởi động luồng nền
threading.Thread(target=_cloud_background_loop, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def index_dashboard():
    """Giao diện Web Dashboard trực quan theo dõi đếm ngược trên điện thoại và PC."""
    now_vn = datetime.datetime.now(VN_TZ).strftime("%H:%M:%S %d/%m/%Y")
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dragon City Battle Timer - Cloud Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #12141A;
            --bg-card: #1A1D26;
            --border: #2D3446;
            --primary: #6366F1;
            --warning: #F59E0B;
            --success: #10B981;
            --danger: #EF4444;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 600px;
            width: 100%;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }}
        .header h1 {{ font-size: 18px; font-weight: 700; }}
        .header p {{ font-size: 12px; color: var(--text-muted); }}
        .countdown-box {{
            text-align: center;
            background: #0F1116;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 24px 16px;
            margin-bottom: 16px;
        }}
        .clock {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 42px;
            font-weight: 700;
            color: var(--warning);
            letter-spacing: 2px;
        }}
        .status-badge {{
            display: inline-block;
            background: rgba(245, 158, 11, 0.15);
            color: var(--warning);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .info-row span:first-child {{ color: var(--text-muted); }}
        .btn {{
            display: inline-block;
            width: 100%;
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            text-align: center;
            transition: 0.2s;
        }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-test {{
            background: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--success);
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span style="font-size: 32px;">⚔️</span>
            <div>
                <h1>Dragon City Battle Timer</h1>
                <p>Cloud Server • Múi giờ Việt Nam (UTC+7): {now_vn}</p>
            </div>
        </div>

        <div class="card">
            <div class="countdown-box">
                <div class="status-badge" id="timerStatus">ĐANG CHỜ DỮ LIỆU...</div>
                <div class="clock" id="timerDisplay">--:--:--</div>
                <p id="targetTimeStr" style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">Đang tải...</p>
            </div>

            <div class="info-row">
                <span>Nhiệm vụ</span>
                <span id="taskName">Đánh rồng Battle</span>
            </div>
            <div class="info-row">
                <span>Discord Webhook</span>
                <span style="color: var(--success);">Đã kết nối ●</span>
            </div>
            <div class="info-row">
                <span>Trạng thái Cron-job</span>
                <span style="color: var(--cyan, #38BDF8);">Tự động đánh thức</span>
            </div>
        </div>

        <button class="btn btn-test" onclick="sendTestWebhook()">🔔 Bắn Tin Nhắn Test Discord Về Điện Thoại</button>
    </div>

    <script>
        let targetTimestamp = 0;

        async function fetchStatus() {{
            try {{
                const res = await fetch('/api/timers');
                const data = await res.json();
                if (data.active_timer) {{
                    const t = data.active_timer;
                    targetTimestamp = t.target_timestamp;
                    document.getElementById('taskName').innerText = t.task_name;
                    document.getElementById('targetTimeStr').innerText = 'Giờ thông báo: ' + t.target_str;
                    if (t.status === 'running') {{
                        document.getElementById('timerStatus').innerText = '⏳ ĐANG ĐẾM NGƯỢC';
                        document.getElementById('timerStatus').style.color = '#F59E0B';
                    }} else if (t.status === 'completed') {{
                        document.getElementById('timerStatus').innerText = '🚨 ĐÃ HẾT GIỜ! DISCORD ĐÃ GỬI CHUÔNG';
                        document.getElementById('timerStatus').style.color = '#EF4444';
                    }}
                }} else {{
                    targetTimestamp = 0;
                    document.getElementById('timerDisplay').innerText = '00:00:00';
                    document.getElementById('timerStatus').innerText = '✅ CHƯA CÓ LỊCH HẸN';
                    document.getElementById('targetTimeStr').innerText = 'Kích hoạt từ Dragon City Bot PC';
                }}
            }} catch(e) {{
                console.error(e);
            }}
        }}

        function updateClock() {{
            if (targetTimestamp > 0) {{
                const nowSec = Date.now() / 1000;
                let rem = Math.floor(targetTimestamp - nowSec);
                if (rem < 0) rem = 0;

                const h = Math.floor(rem / 3600);
                const m = Math.floor((rem % 3600) / 60);
                const s = rem % 60;
                document.getElementById('timerDisplay').innerText = 
                    String(h).padStart(2, '0') + ':' + 
                    String(m).padStart(2, '0') + ':' + 
                    String(s).padStart(2, '0');
            }}
        }}

        async function sendTestWebhook() {{
            try {{
                const res = await fetch('/api/test-webhook', {{ method: 'POST' }});
                const d = await res.json();
                alert(d.message);
            }} catch(e) {{
                alert('Lỗi: ' + e);
            }}
        }}

        fetchStatus();
        setInterval(fetchStatus, 15000);
        setInterval(updateClock, 1000);
    </script>
</body>
</html>"""


@app.post("/api/set-timer")
def set_timer(req: TimerCreateRequest):
    """
    Nhận dữ liệu từ Dragon City Bot Desktop để thiết lập lịch hẹn trên Cloud.
    """
    now = time.time()
    timer_id = req.id or f"timer_{int(now)}"
    target_ts = req.target_timestamp or (now + req.duration_seconds)
    target_dt_vn = datetime.datetime.fromtimestamp(target_ts, VN_TZ)

    hours = req.duration_seconds // 3600
    minutes = (req.duration_seconds % 3600) // 60
    seconds = req.duration_seconds % 60
    duration_str = f"{hours}h {minutes}m {seconds}s"

    timer_obj = {
        "id": timer_id,
        "task_name": req.task_name or "Đánh rồng Battle (Heroic Race)",
        "created_at": now,
        "duration_seconds": req.duration_seconds,
        "duration_str": duration_str,
        "target_timestamp": target_ts,
        "target_str": target_dt_vn.strftime("%H:%M:%S ngày %d/%m/%Y"),
        "discord_webhook": req.discord_webhook or DEFAULT_DISCORD_WEBHOOK,
        "ping_everyone": req.ping_everyone,
        "status": "running",
        "notified": False
    }

    timers_db["active"] = timer_obj
    save_cloud_timers()
    print(f"[CloudServer] ✅ Đã thiết lập timer: {duration_str}. Đích đến (VN): {timer_obj['target_str']}")

    return {
        "status": "success",
        "message": f"Đã lưu lịch hẹn cho {timer_obj['task_name']}",
        "timer": timer_obj
    }


@app.get("/api/cron")
def cron_trigger(key: Optional[str] = Query(None)):
    """
    Endpoint kích hoạt định kỳ từ cron-job.org (mỗi 1-5 phút).
    Đánh thức server Render và kiểm tra bắn Discord Webhook nếu đã tới giờ!
    """
    now = time.time()
    active = timers_db.get("active")

    if not active:
        return {"status": "ok", "message": "Server Render awake, no active timer."}

    if active.get("status") == "running" and not active.get("notified", False):
        target = active.get("target_timestamp", 0)
        # Nếu đã đến giờ (hoặc sớm hơn 30 giây để bao trọn khung cron)
        if now >= (target - 30):
            success = send_discord_alert(active)
            active["status"] = "completed"
            active["notified"] = True
            save_cloud_timers()
            return {
                "status": "triggered",
                "message": "Timer expired! Discord webhook sent.",
                "discord_success": success
            }

    rem = int(active.get("target_timestamp", 0) - now)
    return {
        "status": "running",
        "remaining_seconds": max(0, rem),
        "target_str": active.get("target_str")
    }


@app.get("/api/timers")
def get_timers():
    """Trả về trạng thái timer hiện tại."""
    active = timers_db.get("active")
    return {"active_timer": active}


@app.delete("/api/timers")
def cancel_timer():
    """Hủy bộ hẹn giờ."""
    timers_db.pop("active", None)
    save_cloud_timers()
    return {"status": "cancelled"}


@app.post("/api/test-webhook")
def test_webhook(req: Optional[WebhookTestRequest] = None):
    """Test bắn webhook sang Discord."""
    url = (req.webhook_url if req and req.webhook_url else None) or DEFAULT_DISCORD_WEBHOOK
    dummy_timer = {
        "discord_webhook": url,
        "task_name": "Test Webhook",
        "duration_str": "Test thử nghiệm",
        "ping_everyone": False
    }
    ok = send_discord_alert(dummy_timer)
    return {"success": ok, "message": "Đã bắn tin nhắn test Discord!" if ok else "Gửi webhook thất bại, hãy kiểm tra URL."}
