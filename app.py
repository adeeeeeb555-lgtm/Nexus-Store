"""
===================================================================
 NEXUS HOSTING • Next-Gen Discord Bot Cloud Platform
 Rights & Copyrights © Nexus Store - All Rights Reserved
===================================================================
"""
import os
import json
import time
import requests
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nexus_super_secret_key_123")

# ==================== إعدادات تطبيق ديسكورد OAuth2 ====================
CLIENT_ID = "1557517949001007104"
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "2ZlOW2-lFDEUi8l-axCiJApzlCopidgM")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://nexus-store-6ktz.onrender.com/callback")

DISCORD_API_BASE = "https://discord.com/api/v10"
OAUTH2_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20email%20guilds"

# ==================== قواعد البيانات المحلية ====================
BASE = Path(__file__).resolve().parent
USERS_FILE = BASE / "users_db.json"
BOTS_FILE = BASE / "user_bots.json"
LOGS_FILE = BASE / "bot_logs.json"
ENVS_FILE = BASE / "bot_envs.json"

def load_data(file_path):
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_data(file_path, data):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_bot_log(bot_idx, message):
    logs = load_data(LOGS_FILE)
    key = str(bot_idx)
    if key not in logs:
        logs[key] = []
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    logs[key].append(f"{timestamp} {message}")
    if len(logs[key]) > 50:
        logs[key].pop(0)
    save_data(LOGS_FILE, logs)

# ==================== محاكي الذكاء الاصطناعي لتحليل المشاكل ====================
def ai_diagnose_issue(log_text, bot_name, lang):
    log_lower = (log_text or "").lower()
    if "loginfailure" in log_lower or "token" in log_lower or "unauthorized" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** التوكن الخاص بـ ({bot_name}) برمجة ({lang}) غير صحيح أو منتهي. تحقق من إعدادات التوكن."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** البوت يفتقد لصلاحيات الـ Intents في Discord Developer Portal (فعّل Message Content و Server Members)."
    elif "modulenotfound" in log_lower or "cannot find module" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** توجد مكتبة برمجية ناقصة لم يتم تثبيتها للغة ({lang}). تحقق من ملف المتطلبات."
    else:
        return f"✅ **تحليل الذكاء الاصطناعي (AI):** البوت ({bot_name}) بلغة ({lang}) يعمل بشكل مستقر ولا توجد أخطاء حرجة."

# ==================== تصميم الواجهة الشامل (HTML & CSS & JS) ====================
HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus Cloud Hosting — منصة استضافة بوتات ديسكورد</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<style>
:root {
  --bg: #090c10;
  --panel: #111620;
  --panel-border: #1f2937;
  --primary-purple: #8b5cf6;
  --neon-blue: #38bdf8;
  --neon-green: #22c55e;
  --neon-red: #ef4444;
  --accent-gold: #f3bd45;
  --text-main: #f3f4f6;
  --text-muted: #9ca3af;
}

body {
  margin: 0;
  background: radial-gradient(circle at 50% -20%, #1e1b4b 0%, var(--bg) 60%);
  color: var(--text-main);
  font-family: 'IBM Plex Sans Arabic', sans-serif;
  min-height: 100vh;
}

a { text-decoration: none; }
.shell { max-width: 1400px; margin: auto; padding: 20px; }

/* Topbar Header */
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 0; border-bottom: 1px solid var(--panel-border); margin-bottom: 25px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-purple), var(--neon-blue));
  display: grid; place-items: center; color: white; font-size: 20px;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
}
.brand h1 { font-size: 20px; font-weight: 800; margin: 0; background: linear-gradient(to right, #fff, var(--neon-blue)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.brand small { display: block; color: var(--text-muted); font-size: 11px; }

/* Landing Page Visuals */
.hero-landing { text-align: center; padding: 60px 20px; }
.hero-landing h1 { font-size: 42px; font-weight: 800; margin-bottom: 20px; line-height: 1.3; }
.hero-landing h1 span { color: var(--neon-blue); }
.hero-landing p { color: var(--text-muted); font-size: 18px; max-width: 650px; margin: 0 auto 30px; }
.btn-cta-discord {
  background: linear-gradient(135deg, #5865F2, #404EED); color: white;
  padding: 14px 32px; border-radius: 14px; font-weight: 800; font-size: 18px;
  box-shadow: 0 10px 25px rgba(88, 101, 242, 0.4); transition: 0.2s; display: inline-flex; align-items: center; gap: 10px;
}
.btn-cta-discord:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(88, 101, 242, 0.6); color: white; }

/* Pricing Tables */
.pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 50px; }
.price-card { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 18px; padding: 25px; text-align: center; position: relative; }
.price-card.featured { border-color: var(--primary-purple); box-shadow: 0 0 30px rgba(139, 92, 246, 0.2); }
.badge-featured { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--primary-purple); color: white; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 700; }

/* Dashboard Layout */
.dash-layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 20px; }
.sidebar-panel { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 18px; padding: 20px; }
.main-panel { background: var(--panel); border: 1px solid var(--panel-border); border-radius: 18px; padding: 25px; }

/* Bot List Items */
.bot-item {
  display: block; padding: 12px 15px; border-radius: 12px; border: 1px solid var(--panel-border);
  background: #0d1117; color: var(--text-main); margin-bottom: 10px; transition: 0.2s;
}
.bot-item:hover, .bot-item.active { border-color: var(--neon-blue); background: #161b22; }

/* Control Action Buttons */
.btn-action-start { background: rgba(34, 197, 94, 0.15); color: var(--neon-green); border: 1px solid var(--neon-green); font-weight: 700; }
.btn-action-start:hover { background: var(--neon-green); color: black; }
.btn-action-stop { background: rgba(239, 68, 68, 0.15); color: var(--neon-red); border: 1px solid var(--neon-red); font-weight: 700; }
.btn-action-stop:hover { background: var(--neon-red); color: white; }
.btn-action-restart { background: rgba(56, 189, 248, 0.15); color: var(--neon-blue); border: 1px solid var(--neon-blue); font-weight: 700; }
.btn-action-restart:hover { background: var(--neon-blue); color: black; }

/* Monitors & Gauge Cards */
.monitors-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
.monitor-card { background: #0d1117; border: 1px solid var(--panel-border); border-radius: 14px; padding: 15px; }
.monitor-card h6 { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
.monitor-card .value { font-size: 20px; font-weight: 800; }

/* Nav Tabs Custom */
.nav-tabs-custom { display: flex; gap: 10px; border-bottom: 1px solid var(--panel-border); margin-bottom: 20px; padding-bottom: 10px; }
.nav-tab-btn { background: transparent; border: none; color: var(--text-muted); font-weight: 700; padding: 8px 16px; border-radius: 10px; cursor: pointer; }
.nav-tab-btn.active { background: rgba(56, 189, 248, 0.1); color: var(--neon-blue); border: 1px solid var(--neon-blue); }

/* Console Screen */
.console-screen {
  background: #05070a; color: var(--neon-green); font-family: 'Courier New', monospace;
  padding: 15px; border-radius: 12px; border: 1px solid var(--panel-border);
  height: 250px; overflow-y: auto; font-size: 13px; line-height: 1.6; direction: ltr; text-align: left;
}

/* File Manager Table */
.file-table { width: 100%; color: var(--text-main); font-size: 14px; }
.file-table th { color: var(--text-muted); border-bottom: 1px solid var(--panel-border); padding: 10px; text-align: right; }
.file-table td { padding: 12px 10px; border-bottom: 1px solid #161b22; }

footer { border-top: 1px solid var(--panel-border); margin-top: 40px; padding: 20px 0; text-align: center; color: var(--text-muted); font-size: 12px; }
</style>
</head>
<body>
<div class="shell">

<!-- Header Topbar -->
<header class="topbar">
  <a href="/" class="brand">
    <div class="brand-icon"><i class="fa-solid fa-server"></i></div>
    <div>
      <h1>NEXUS CLOUD</h1>
      <small>Next-Gen Discord Bot Hosting</small>
    </div>
  </a>
  {% if user %}
  <div class="d-flex align-items-center gap-3">
    <div class="d-flex align-items-center gap-2">
      <img src="{{ user.avatar_url }}" width="36" height="36" class="rounded-circle border border-primary">
      <span class="fw-bold">{{ user.username }}</span>
    </div>
    <a href="/logout" class="btn btn-outline-danger btn-sm"><i class="fa-solid fa-power-off"></i></a>
  </div>
  {% else %}
  <a href="/login" class="btn btn-cta-discord" style="padding:8px 18px; font-size:14px;"><i class="fa-brands fa-discord"></i> تسجيل الدخول</a>
  {% endif %}
</header>

{% if not user %}
<!-- Landing Page الواجهة الخارجية قبل تسجيل الدخول -->
<div class="hero-landing">
  <h1>استضافة بوتات ديسكورد <span>فائقة السرعة</span> والمستقبلية</h1>
  <p>احصل على أداء استثنائي لبوتاتك مع مراقبة الموارد المباشرة، محرر الملفات المدمج، والذكاء الاصطناعي لتشخيص الأخطاء.</p>
  <a href="/login" class="btn-cta-discord"><i class="fa-brands fa-discord"></i> ابدأ الآن مجاناً عبر Discord</a>

  <!-- Pricing Table جدول الأسعار والموارد -->
  <div class="pricing-grid">
    <div class="price-card">
      <h4 class="fw-bold">الخطة المجانية (Free)</h4>
      <h2 class="my-3">$0 <small class="fs-6 text-muted">/شهرياً</small></h2>
      <ul class="list-unstyled text-start text-muted lh-lg mb-4 fs-6">
        <li><i class="fa-solid fa-check text-success me-2"></i> الذاكرة (RAM): <strong>512 MB</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> المعالج (CPU): <strong>50% vCPU</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> التخزين: <strong>1 GB NVMe</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> قاعدة بيانات مدمجة</li>
      </ul>
      <a href="/login" class="btn btn-outline-light w-100 fw-bold">تجربة الآن</a>
    </div>

    <div class="price-card featured">
      <span class="badge-featured">الأكثر شعبية</span>
      <h4 class="fw-bold text-primary">الخطة الاحترافية (Pro)</h4>
      <h2 class="my-3">$4.99 <small class="fs-6 text-muted">/شهرياً</small></h2>
      <ul class="list-unstyled text-start text-muted lh-lg mb-4 fs-6">
        <li><i class="fa-solid fa-check text-success me-2"></i> الذاكرة (RAM): <strong>2048 MB (2GB)</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> المعالج (CPU): <strong>150% vCPU</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> التخزين: <strong>10 GB NVMe SSD</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> قاعدة بيانات MongoDB / MySQL</li>
        <li><i class="fa-solid fa-check text-success me-2"></i> تشغيل 24/7 بدون انقطاع</li>
      </ul>
      <a href="/login" class="btn btn-primary w-100 fw-bold">ترقية للبروفيشينال</a>
    </div>
  </div>
</div>
{% else %}

<!-- Dashboard Internal لوحة التحكم الداخلية -->
<div class="dash-layout">
  <!-- القائمة الجانبية Sidebar -->
  <div class="sidebar-panel">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-bold m-0"><i class="fa-solid fa-robot text-primary me-2"></i>بوتاتي ({{ user_bots|length }})</h6>
      <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addBotModal"><i class="fa-solid fa-plus"></i></button>
    </div>
    <div class="bot-list">
      {% for bot in user_bots %}
      <a href="/?bot={{ loop.index0 }}" class="bot-item {% if selected_bot_idx == loop.index0 %}active{% endif %}">
        <div class="d-flex justify-content-between align-items-center">
          <span class="fw-bold">{{ bot.name }}</span>
          <span class="badge {% if bot.status == 'شغال' %}bg-success{% else %}bg-danger{% endif %}">{{ bot.status }}</span>
        </div>
        <small class="text-muted d-block mt-1">{{ bot.lang }} • Prefix: {{ bot.prefix }}</small>
      </a>
      {% else %}
      <p class="text-muted text-center py-4 fs-6">لا توجد بوتات مضافة بعد.</p>
      {% endfor %}
    </div>
  </div>

  <!-- المنطقة الرئيسية Main Panel -->
  <div class="main-panel">
    {% if active_bot %}
    <!-- أزرار التحكم الفوري Action Buttons -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold m-0">{{ active_bot.name }}</h3>
        <small class="text-muted">اللغة: {{ active_bot.lang }} | البريفكس: {{ active_bot.prefix }}</small>
      </div>
      <div class="d-flex gap-2">
        <a href="/bot_action/{{ selected_bot_idx }}/start" class="btn btn-action-start"><i class="fa-solid fa-play me-1"></i> تشغيل</a>
        <a href="/bot_action/{{ selected_bot_idx }}/stop" class="btn btn-action-stop"><i class="fa-solid fa-stop me-1"></i> إيقاف</a>
        <a href="/bot_action/{{ selected_bot_idx }}/restart" class="btn btn-action-restart"><i class="fa-solid fa-rotate me-1"></i> إعادة تشغيل</a>
      </div>
    </div>

    <!-- الأقسام Tabs Navigation -->
    <div class="nav-tabs-custom">
      <button class="nav-tab-btn active" onclick="showTab('overviewTab', this)"><i class="fa-solid fa-chart-pie me-1"></i> الرئيسية (Overview)</button>
      <button class="nav-tab-btn" onclick="showTab('consoleTab', this)"><i class="fa-solid fa-terminal me-1"></i> وحدة التحكم (Console)</button>
      <button class="nav-tab-btn" onclick="showTab('filesTab', this)"><i class="fa-solid fa-folder me-1"></i> مدير الملفات</button>
      <button class="nav-tab-btn" onclick="showTab('envTab', this)"><i class="fa-solid fa-key me-1"></i> المتغيرات (.env)</button>
      <button class="nav-tab-btn" onclick="showTab('dbTab', this)"><i class="fa-solid fa-database me-1"></i> قاعدة البيانات</button>
    </div>

    <!-- Tab 1: Overview الرئيسية -->
    <div id="overviewTab" class="tab-content">
      <div class="monitors-grid">
        <div class="monitor-card">
          <h6>استهلاك الـ RAM</h6>
          <div class="value text-primary">{% if active_bot.status == 'شغال' %}124 MB / 512 MB{% else %}0 MB{% endif %}</div>
        </div>
        <div class="monitor-card">
          <h6>استهلاك الـ CPU</h6>
          <div class="value text-info">{% if active_bot.status == 'شغال' %}1.2%{% else %}0%{% endif %}</div>
        </div>
        <div class="monitor-card">
          <h6>مساحة الـ NVMe Disk</h6>
          <div class="value text-warning">45 MB / 1 GB</div>
        </div>
      </div>

      <div class="p-3 bg-dark rounded border border-secondary mb-3">
        <h6 class="fw-bold text-warning mb-2"><i class="fa-solid fa-wand-magic-sparkles me-2"></i>تشخيص الذكاء الاصطناعي (AI Diagnostics)</h6>
        <p class="m-0 fs-6">{{ ai_diagnosis }}</p>
      </div>
    </div>

    <!-- Tab 2: Console وحدة التحكم بالسطور -->
    <div id="consoleTab" class="tab-content d-none">
      <div class="console-screen" id="consoleLogs">{% for log in bot_logs %}{{ log }}
{% else %}[Nexus Hosting System] السجلات جاهزة. اضغط على تشغيل للبدء...
{% endfor %}</div>
    </div>

    <!-- Tab 3: File Manager مدير الملفات -->
    <div id="filesTab" class="tab-content d-none">
      <table class="file-table">
        <thead>
          <tr>
            <th>اسم الملف</th>
            <th>الحجم</th>
            <th>نوع الملف</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><i class="fa-solid fa-file-code text-warning me-2"></i> main.py (أو index.js)</td>
            <td>4.2 KB</td>
            <td>ملف الكود الرئيسي</td>
          </tr>
          <tr>
            <td><i class="fa-solid fa-file-lines text-info me-2"></i> requirements.txt</td>
            <td>120 B</td>
            <td>ملف المكتبات</td>
          </tr>
          <tr>
            <td><i class="fa-solid fa-lock text-danger me-2"></i> .env</td>
            <td>85 B</td>
            <td>ملف المتغيرات السرية</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Tab 4: Environment Variables المتغيرات البيئية -->
    <div id="envTab" class="tab-content d-none">
      <div class="p-3 bg-dark rounded border border-secondary">
        <h6 class="fw-bold mb-3"><i class="fa-solid fa-key text-warning me-2"></i>متغيرات البيئة (.env)</h6>
        <div class="row g-2 mb-2">
          <div class="col-5"><input type="text" class="form-control bg-secondary text-white border-0" value="BOT_TOKEN" readonly></div>
          <div class="col-7"><input type="password" class="form-control bg-secondary text-white border-0" value="••••••••••••••••••••" readonly></div>
        </div>
      </div>
    </div>

    <!-- Tab 5: Database قاعدة البيانات المدمجة -->
    <div id="dbTab" class="tab-content d-none">
      <div class="p-3 bg-dark rounded border border-secondary text-center py-4">
        <i class="fa-solid fa-database display-4 text-primary mb-3"></i>
        <h5 class="fw-bold">قاعدة بيانات MongoDB المدمجة</h5>
        <p class="text-muted">يمكنك الربط بقاعدة بيانات مجانية وسريعة مخصصة لبوتك بضغطة زر واحدة.</p>
        <button class="btn btn-outline-primary btn-sm">إنشاء قاعدة بيانات جديدة</button>
      </div>
    </div>

    {% else %}
    <div class="text-center py-5">
      <i class="fa-solid fa-hand-pointer display-4 text-muted mb-3"></i>
      <h4 class="fw-bold">اختر بوت من القائمة الجانبية</h4>
      <p class="text-muted">الرجاء تحديد أحد بوتاتك للتحكم الكامل المباشر به.</p>
    </div>
    {% endif %}
  </div>
</div>
{% endif %}

<footer>© 2026 Nexus Cloud Platform — جميع الحقوق محفوظة</footer>
</div>

<!-- Modal: إضافة بوت -->
{% if user %}
<div class="modal fade" id="addBotModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content bg-dark text-white border-secondary">
      <div class="modal-header border-secondary">
        <h5 class="modal-title fw-bold">إضافة بوت جديد</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form action="/add_bot" method="POST">
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">اسم البوت</label>
            <input type="text" name="name" class="form-control bg-secondary text-white border-0" required>
          </div>
          <div class="mb-3">
            <label class="form-label">توكن البوت (Bot Token)</label>
            <input type="password" name="token" class="form-control bg-secondary text-white border-0" required>
          </div>
          <div class="mb-3">
            <label class="form-label">بادئة الأوامر (Prefix)</label>
            <input type="text" name="prefix" value="!" class="form-control bg-secondary text-white border-0">
          </div>
          <div class="mb-3">
            <label class="form-label">لغة البرمجة</label>
            <select name="lang" class="form-select bg-secondary text-white border-0">
              <option value="Python">Python</option>
              <option value="JavaScript (Node.js)">JavaScript (Node.js)</option>
              <option value="Lua">Lua</option>
              <option value="TypeScript">TypeScript</option>
            </select>
          </div>
        </div>
        <div class="modal-footer border-secondary">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
          <button type="submit" class="btn btn-primary">حفظ وإضافة</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function showTab(tabId, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('d-none'));
  document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.remove('d-none');
  btn.classList.add('active');
}
const consoleBox = document.getElementById('consoleLogs');
if(consoleBox) consoleBox.scrollTop = consoleBox.scrollHeight;
</script>
</body>
</html>
"""

# ==================== المسارات والتحكم (Routes) ====================

@app.route('/')
def index():
    user = session.get('user')
    user_bots = []
    active_bot = None
    bot_logs = []
    ai_diagnosis = "لم يتم رصد أخطاء."
    selected_bot_idx = request.args.get('bot', type=int)

    if user:
        all_bots = load_data(BOTS_FILE)
        user_bots = all_bots.get(user['id'], [])
        
        if user_bots:
            if selected_bot_idx is not None and 0 <= selected_bot_idx < len(user_bots):
                active_bot = user_bots[selected_bot_idx]
                all_logs = load_data(LOGS_FILE)
                bot_logs = all_logs.get(str(selected_bot_idx), [])
                combined_logs = "\n".join(bot_logs)
                ai_diagnosis = ai_diagnose_issue(combined_logs, active_bot['name'], active_bot['lang'])

    return render_template_string(
        HTML_TEMPLATE, 
        user=user, 
        user_bots=user_bots, 
        active_bot=active_bot, 
        selected_bot_idx=selected_bot_idx,
        bot_logs=bot_logs,
        ai_diagnosis=ai_diagnosis
    )

@app.route('/login')
def login():
    return redirect(OAUTH2_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('index'))

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(f"{DISCORD_API_BASE}/oauth2/token", data=data, headers=headers)
    token_json = res.json()
    access_token = token_json.get('access_token')

    if not access_token:
        return "حدث خطأ أثناء المصادقة مع ديسكورد", 400

    user_res = requests.get(f"{DISCORD_API_BASE}/users/@me", headers={'Authorization': f'Bearer {access_token}'})
    user_data = user_res.json()

    user_id = user_data['id']
    avatar_hash = user_data.get('avatar')
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png" if avatar_hash else "https://cdn.discordapp.com/embed/avatars/0.png"

    user_info = {
        'id': user_id,
        'username': user_data.get('username'),
        'email': user_data.get('email'),
        'avatar_url': avatar_url
    }

    session['user'] = user_info
    users = load_data(USERS_FILE)
    users[user_id] = user_info
    save_data(USERS_FILE, users)

    return redirect(url_for('index'))

@app.route('/add_bot', methods=['POST'])
def add_bot():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    bot_name = request.form.get('name')
    bot_token = request.form.get('token')
    bot_prefix = request.form.get('prefix', '!')
    bot_lang = request.form.get('lang', 'Python')

    all_bots = load_data(BOTS_FILE)
    if user['id'] not in all_bots:
        all_bots[user['id']] = []

    new_bot_idx = len(all_bots[user['id']])
    all_bots[user['id']].append({
        'name': bot_name,
        'token': bot_token,
        'prefix': bot_prefix,
        'lang': bot_lang,
        'status': 'متوقف'
    })

    save_data(BOTS_FILE, all_bots)
    add_bot_log(new_bot_idx, f"تم إنشاء وإضافة البوت بلغة ({bot_lang}).")
    return redirect(url_for('index', bot=new_bot_idx))

@app.route('/bot_action/<int:bot_idx>/<action>')
def bot_action(bot_idx, action):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(user['id'], [])

    if bot_idx < len(user_bots):
        bot = user_bots[bot_idx]
        if action == 'start':
            bot['status'] = 'شغال'
            add_bot_log(bot_idx, f"▶️ تم بدء تشغيل البوت ({bot['name']}).")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(bot_idx, f"⏹️ تم إيقاف البوت ({bot['name']}).")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(bot_idx, f"🔄 جاري إعادة تشغيل البوت ({bot['name']})...")
        
        save_data(BOTS_FILE, all_bots)

    return redirect(url_for('index', bot=bot_idx))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
