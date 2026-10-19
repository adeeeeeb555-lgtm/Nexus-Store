"""
===================================================================
 NEXUS CLOUD HOSTING • Ultimate Enterprise Discord Bot Platform
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
app.secret_key = os.environ.get("SECRET_KEY", "nexus_super_secret_enterprise_key_999")

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
    if len(logs[key]) > 100:
        logs[key].pop(0)
    save_data(LOGS_FILE, logs)

# ==================== محاكي الذكاء الاصطناعي لتحليل المشاكل ====================
def ai_diagnose_issue(log_text, bot_name, lang):
    log_lower = (log_text or "").lower()
    if "loginfailure" in log_lower or "token" in log_lower or "unauthorized" in log_lower:
        return f"⚠️ **تقرير الذكاء الاصطناعي (AI):** التوكن الخاص بـ ({bot_name}) بلغة ({lang}) خاطئ أو منتهي الصلاحية. يرجى التحقق من إعدادات الـ Token."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"⚠️ **تقرير الذكاء الاصطناعي (AI):** البوت يفتقر لصلاحيات الـ Intents الضرورية في بوابة المطورين (Discord Developer Portal)."
    elif "modulenotfound" in log_lower or "cannot find module" in log_lower:
        return f"⚠️ **تقرير الذكاء الاصطناعي (AI):** هناك مكتبة برمجية ناقصة أو غير مثبتة لبيئة تشغيل ({lang}). تأكد من إضافتها."
    else:
        return f"✅ **تقرير الذكاء الاصطناعي (AI):** البوت ({bot_name}) يعمل بشكل مثالي ضمن بيئة استضافة Nexus Cloud ولا توجد أي مشاكل ظاهرة."

# ==================== تصميم الواجهة الاحترافي الكامل (HTML & CSS & JS) ====================
HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus Cloud Hosting — Enterprise Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<style>
:root {
  --bg-dark: #07090e;
  --panel-bg: #0d1117;
  --panel-border: #21262d;
  --primary-glow: #8b5cf6;
  --neon-blue: #38bdf8;
  --neon-green: #238636;
  --neon-red: #da3633;
  --accent-gold: #f3bd45;
  --text-light: #f0f6fc;
  --text-muted: #8b949e;
}

body {
  margin: 0;
  background-color: var(--bg-dark);
  background-image: radial-gradient(circle at 50% -20%, #161b22 0%, var(--bg-dark) 70%);
  color: var(--text-light);
  font-family: 'IBM Plex Sans Arabic', sans-serif;
  min-height: 100vh;
}

a { text-decoration: none; color: inherit; }
.container-xl { max-width: 1440px; margin: auto; padding: 24px; }

/* Top Header Navbar */
.navbar-nexus {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; background: var(--panel-bg); border: 1px solid var(--panel-border);
  border-radius: 16px; margin-bottom: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.brand-box { display: flex; align-items: center; gap: 14px; }
.brand-logo {
  width: 46px; height: 46px; border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  display: grid; place-items: center; color: white; font-size: 22px;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
}
.brand-title h1 { font-size: 20px; font-weight: 800; margin: 0; letter-spacing: 0.5px; }
.brand-title small { color: var(--text-muted); font-size: 11px; display: block; }

/* Landing Hero Section */
.hero-section { text-align: center; padding: 70px 20px; }
.hero-section h1 { font-size: 46px; font-weight: 800; line-height: 1.3; margin-bottom: 20px; }
.hero-section h1 span { color: var(--neon-blue); }
.hero-section p { color: var(--text-muted); font-size: 18px; max-width: 700px; margin: 0 auto 35px; line-height: 1.8; }
.btn-discord-login {
  background: #5865F2; color: white; padding: 14px 35px; border-radius: 12px;
  font-weight: 800; font-size: 17px; display: inline-flex; align-items: center; gap: 12px;
  box-shadow: 0 10px 30px rgba(88, 101, 242, 0.4); transition: 0.2s; border: none;
}
.btn-discord-login:hover { background: #4752c4; transform: translateY(-2px); color: white; }

/* Pricing Cards */
.pricing-wrapper { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 60px; text-align: right; }
.price-box { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 20px; padding: 30px; position: relative; }
.price-box.highlight { border-color: #6366f1; box-shadow: 0 0 30px rgba(99, 102, 241, 0.2); }
.badge-plan { position: absolute; top: -14px; right: 30px; background: #6366f1; color: white; font-size: 12px; padding: 5px 14px; border-radius: 20px; font-weight: 700; }

/* Dashboard Workspace Layout */
.workspace-grid { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 24px; }
.sidebar-box { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 18px; padding: 22px; height: fit-content; }
.content-box { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 18px; padding: 30px; }

/* Bots List UI */
.bot-card-item {
  display: block; padding: 14px 16px; border-radius: 12px; border: 1px solid var(--panel-border);
  background: #161b22; color: var(--text-light); margin-bottom: 12px; transition: 0.2s;
}
.bot-card-item:hover, .bot-card-item.active { border-color: var(--neon-blue); background: #1c2128; transform: translateX(-3px); }

/* Control Action Buttons */
.btn-cmd-start { background: rgba(35, 134, 54, 0.2); color: #3fb950; border: 1px solid #238636; font-weight: 700; padding: 8px 18px; border-radius: 10px; }
.btn-cmd-start:hover { background: #238636; color: white; }
.btn-cmd-stop { background: rgba(218, 54, 51, 0.2); color: #f85149; border: 1px solid #da3633; font-weight: 700; padding: 8px 18px; border-radius: 10px; }
.btn-cmd-stop:hover { background: #da3633; color: white; }
.btn-cmd-restart { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; font-weight: 700; padding: 8px 18px; border-radius: 10px; }
.btn-cmd-restart:hover { background: #38bdf8; color: black; }

/* Resource Stat Cards */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 25px; }
.stat-card { background: #161b22; border: 1px solid var(--panel-border); border-radius: 14px; padding: 18px; }
.stat-card span { font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 6px; }
.stat-card strong { font-size: 22px; font-weight: 800; }

/* Navigation Tabs */
.tabs-navigation { display: flex; gap: 10px; border-bottom: 1px solid var(--panel-border); margin-bottom: 25px; padding-bottom: 12px; flex-wrap: wrap; }
.tab-trigger { background: transparent; border: 1px solid var(--panel-border); color: var(--text-muted); font-weight: 700; padding: 10px 20px; border-radius: 12px; cursor: pointer; transition: 0.2s; }
.tab-trigger.active { background: rgba(56, 189, 248, 0.15); color: var(--neon-blue); border-color: var(--neon-blue); }

/* Terminal Console */
.terminal-screen {
  background: #020408; color: #3fb950; font-family: 'Courier New', Courier, monospace;
  padding: 20px; border-radius: 14px; border: 1px solid var(--panel-border);
  height: 320px; overflow-y: auto; font-size: 13.5px; line-height: 1.7; direction: ltr; text-align: left;
  box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
}

/* File Manager Table */
.nexus-table { width: 100%; border-collapse: collapse; }
.nexus-table th { color: var(--text-muted); border-bottom: 1px solid var(--panel-border); padding: 12px; text-align: right; font-size: 13px; }
.nexus-table td { padding: 14px 12px; border-bottom: 1px solid #161b22; font-size: 14px; }

footer { border-top: 1px solid var(--panel-border); margin-top: 50px; padding: 25px 0; text-align: center; color: var(--text-muted); font-size: 13px; }
</style>
</head>
<body>
<div class="container-xl">

<!-- Top Navigation Bar -->
<header class="navbar-nexus">
  <a href="/" class="brand-box">
    <div class="brand-logo"><i class="fa-solid fa-server"></i></div>
    <div class="brand-title">
      <h1>NEXUS CLOUD</h1>
      <small>Enterprise Bot Infrastructure</small>
    </div>
  </a>
  {% if user %}
  <div class="d-flex align-items-center gap-3">
    <div class="d-flex align-items-center gap-2 bg-dark px-3 py-2 rounded-pill border border-secondary">
      <img src="{{ user.avatar_url }}" width="34" height="34" class="rounded-circle border border-primary">
      <span class="fw-bold">{{ user.username }}</span>
    </div>
    <a href="/logout" class="btn btn-outline-danger btn-sm px-3"><i class="fa-solid fa-power-off me-1"></i> خروج</a>
  </div>
  {% else %}
  <a href="/login" class="btn btn-discord-login" style="padding: 10px 20px; font-size: 14px;"><i class="fa-brands fa-discord"></i> تسجيل الدخول</a>
  {% endif %}
</header>

{% if not user %}
<!-- Landing Page الواجهة الخارجية الكاملة لجذب المطورين -->
<div class="hero-section">
  <h1>استضافة بوتات ديسكورد <span>فائقة الاحترافية</span></h1>
  <p>منصة سحابية متكاملة مصممة خصيصاً للمطورين وأصحاب المجتمعات الكبرى. تحكم كامل بالموارد، مراقبة حية، أمان تام، ومساعد ذكاء اصطناعي لحل المشاكل فوراً.</p>
  <a href="/login" class="btn-discord-login"><i class="fa-brands fa-discord"></i> ابدأ الآن مجاناً عبر Discord</a>

  <!-- جدول الأسعار المتقدم -->
  <div class="pricing-grid pricing-wrapper">
    <div class="price-box">
      <h3 class="fw-bold mb-2">الخطة المجانية</h3>
      <h2 class="my-3 text-white">$0 <small class="fs-6 text-muted">/شهرياً</small></h2>
      <p class="text-muted fs-6 mb-4">مثالية للمشاريع الصغيرة وتجارب التطوير الأولى.</p>
      <ul class="list-unstyled text-start text-muted lh-lg mb-4">
        <li><i class="fa-solid fa-check text-success me-2"></i> الذاكرة (RAM): <strong>512 MB</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> المعالج: <strong>50% vCPU</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> التخزين: <strong>1 GB NVMe</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> قاعدة بيانات مجانية</li>
      </ul>
      <a href="/login" class="btn btn-outline-light w-100 fw-bold py-2">اختر الخطة</a>
    </div>

    <div class="price-box highlight">
      <span class="badge-plan">الأكثر طلباً</span>
      <h3 class="fw-bold mb-2 text-primary">الخطة الاحترافية (Pro)</h3>
      <h2 class="my-3 text-white">$4.99 <small class="fs-6 text-muted">/شهرياً</small></h2>
      <p class="text-muted fs-6 mb-4">للبوتات الكبيرة التي تتطلب تشغيل مستمر 24/7 دون انقطاع.</p>
      <ul class="list-unstyled text-start text-muted lh-lg mb-4">
        <li><i class="fa-solid fa-check text-success me-2"></i> الذاكرة (RAM): <strong>2048 MB (2GB)</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> المعالج: <strong>150% vCPU</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> التخزين: <strong>10 GB NVMe SSD</strong></li>
        <li><i class="fa-solid fa-check text-success me-2"></i> قواعد بيانات MySQL / MongoDB</li>
        <li><i class="fa-solid fa-check text-success me-2"></i> دعم فني مخصص وأولوية عالية</li>
      </ul>
      <a href="/login" class="btn btn-primary w-100 fw-bold py-2">ترقية الحساب</a>
    </div>
  </div>
</div>
{% else %}

<!-- Dashboard Workspace لوحة التحكم الداخلية الشاملة -->
<div class="workspace-grid">
  <!-- القائمة الجانبية لإدارة البوتات -->
  <div class="sidebar-box">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold m-0"><i class="fa-solid fa-robot text-primary me-2"></i>بوتاتك ({{ user_bots|length }})</h5>
      <button class="btn btn-primary btn-sm px-3" data-bs-toggle="modal" data-bs-target="#addBotModal"><i class="fa-solid fa-plus me-1"></i> إضافة</button>
    </div>
    <div class="bot-list">
      {% for bot in user_bots %}
      <a href="/?bot={{ loop.index0 }}" class="bot-card-item {% if selected_bot_idx == loop.index0 %}active{% endif %}">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <span class="fw-bold">{{ bot.name }}</span>
          <span class="badge {% if bot.status == 'شغال' %}bg-success{% else %}bg-danger{% endif %}">{{ bot.status }}</span>
        </div>
        <small class="text-muted">{{ bot.lang }} • Prefix: {{ bot.prefix }}</small>
      </a>
      {% else %}
      <div class="text-center py-5 text-muted">
        <i class="fa-solid fa-box-open fs-2 mb-2"></i>
        <p class="m-0">لا توجد بوتات مضافة حالياً.</p>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- المحتوى الرئيسي للوحة التحكم والأقسام -->
  <div class="content-box">
    {% if active_bot %}
    <!-- سطر العنوان وأزرار التحكم الفوري -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
      <div>
        <h2 class="fw-bold m-0 text-white">{{ active_bot.name }}</h2>
        <small class="text-muted">بيئة التشغيل: {{ active_bot.lang }} | البادئة: {{ active_bot.prefix }}</small>
      </div>
      <div class="d-flex gap-2">
        <a href="/bot_action/{{ selected_bot_idx }}/start" class="btn-cmd-start"><i class="fa-solid fa-play me-1"></i> تشغيل</a>
        <a href="/bot_action/{{ selected_bot_idx }}/stop" class="btn-cmd-stop"><i class="fa-solid fa-stop me-1"></i> إيقاف</a>
        <a href="/bot_action/{{ selected_bot_idx }}/restart" class="btn-cmd-restart"><i class="fa-solid fa-rotate me-1"></i> إعادة تشغيل</a>
      </div>
    </div>

    <!-- نظام الـ Tabs (الأقسام المتعددة) -->
    <div class="tabs-navigation">
      <button class="tab-trigger active" onclick="switchTab('tabOverview', this)"><i class="fa-solid fa-chart-pie me-2"></i> نظرة عامة (Overview)</button>
      <button class="tab-trigger" onclick="switchTab('tabConsole', this)"><i class="fa-solid fa-terminal me-2"></i> وحدة التحكم (Console)</button>
      <button class="tab-trigger" onclick="switchTab('tabFiles', this)"><i class="fa-solid fa-folder-open me-2"></i> مدير الملفات</button>
      <button class="tab-trigger" onclick="switchTab('tabEnv', this)"><i class="fa-solid fa-key me-2"></i> المتغيرات البيئية (.env)</button>
      <button class="tab-trigger" onclick="switchTab('tabDb', this)"><i class="fa-solid fa-database me-2"></i> قواعد البيانات</button>
    </div>

    <!-- Tab 1: Overview الرئيسية ومراقبة الموارد -->
    <div id="tabOverview" class="tab-pane">
      <div class="stats-grid">
        <div class="stat-card">
          <span>استهلاك الذاكرة العشوائية (RAM)</span>
          <strong class="text-primary">{% if active_bot.status == 'شغال' %}142 MB / 512 MB{% else %}0 MB{% endif %}</strong>
        </div>
        <div class="stat-card">
          <span>استهلاك المعالج (CPU)</span>
          <strong class="text-info">{% if active_bot.status == 'شغال' %}1.8%{% else %}0%{% endif %}</strong>
        </div>
        <div class="stat-card">
          <span>المساحة المستخدمة (NVMe)</span>
          <strong class="text-warning">52 MB / 1 GB</strong>
        </div>
      </div>

      <div class="p-4 bg-dark rounded-4 border border-secondary mt-3">
        <h5 class="fw-bold text-warning mb-3"><i class="fa-solid fa-wand-magic-sparkles me-2"></i>تقرير الذكاء الاصطناعي الذكي (AI Diagnostics)</h5>
        <p class="m-0 text-light fs-6 lh-lg">{{ ai_diagnosis }}</p>
      </div>
    </div>

    <!-- Tab 2: Console الشاشة السوداء والسجلات -->
    <div id="tabConsole" class="tab-pane d-none">
      <div class="terminal-screen" id="terminalLogs">{% for log in bot_logs %}{{ log }}
{% else %}[Nexus Enterprise Core] وحدة السجلات مستعدة بانتظار تشغيل البوت...
{% endfor %}</div>
    </div>

    <!-- Tab 3: File Manager مدير الملفات -->
    <div id="tabFiles" class="tab-pane d-none">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold m-0">ملفات البوت السحابية</h5>
        <button class="btn btn-outline-light btn-sm"><i class="fa-solid fa-upload me-1"></i> رفع ملف جديد</button>
      </div>
      <table class="nexus-table">
        <thead>
          <tr>
            <th>اسم الملف</th>
            <th>الحجم</th>
            <th>نوع العنصر</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><i class="fa-solid fa-file-code text-warning me-2"></i> main.py / index.js</td>
            <td>4.8 KB</td>
            <td>ملف البرمجة الأساسي</td>
          </tr>
          <tr>
            <td><i class="fa-solid fa-file-lines text-info me-2"></i> requirements.txt / package.json</td>
            <td>240 B</td>
            <td>ملف المكتبات والتبعيات</td>
          </tr>
          <tr>
            <td><i class="fa-solid fa-lock text-danger me-2"></i> .env</td>
            <td>95 B</td>
            <td>متغيرات البيئة المؤمّنة</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Tab 4: Environment Variables متغيرات البيئة -->
    <div id="tabEnv" class="tab-pane d-none">
      <div class="p-4 bg-dark rounded-4 border border-secondary">
        <h5 class="fw-bold mb-3"><i class="fa-solid fa-key text-warning me-2"></i>إدارة المتغيرات السرية (.env)</h5>
        <p class="text-muted fs-6 mb-4">قم بتخزين الـ Tokens وأسرار التطبيق بأمان تام خلف طبقة تشفير عالية.</p>
        <div class="row g-3 mb-3">
          <div class="col-md-4"><input type="text" class="form-control bg-secondary text-white border-0" value="DISCORD_BOT_TOKEN" readonly></div>
          <div class="col-md-8"><input type="password" class="form-control bg-secondary text-white border-0" value="••••••••••••••••••••••••••••••" readonly></div>
        </div>
      </div>
    </div>

    <!-- Tab 5: Databases قواعد البيانات -->
    <div id="tabDb" class="tab-pane d-none">
      <div class="p-5 bg-dark rounded-4 border border-secondary text-center">
        <i class="fa-solid fa-database display-3 text-primary mb-3"></i>
        <h4 class="fw-bold mb-2">قاعدة بيانات MongoDB / MySQL المدمجة</h4>
        <p class="text-muted col-md-8 mx-auto mb-4">أنشئ قاعدة بيانات خاصة ببوتك بضغطة زر واحدة واحصل على رابط الاتصال (Connection URI) الفوري للاستخدام في كودك.</p>
        <button class="btn btn-primary px-4 fw-bold">إنشاء قاعدة بيانات جديدة</button>
      </div>
    </div>

    {% else %}
    <div class="text-center py-5">
      <i class="fa-solid fa-hand-pointer display-3 text-muted mb-3"></i>
      <h3 class="fw-bold">اختر بوت من القائمة الجانبية</h3>
      <p class="text-muted fs-6">الرجاء اختيار أحد بوتاتك أو إنشاء بوت جديد للتحكم بكافة الميزات والإعدادات.</p>
    </div>
    {% endif %}
  </div>
</div>
{% endif %}

<footer>© 2026 Nexus Cloud Platform — جميع الحقوق محفوظة لـ Nexus Store</footer>
</div>

<!-- Modal إضافة بوت جديد -->
{% if user %}
<div class="modal fade" id="addBotModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content bg-dark text-white border-secondary rounded-4">
      <div class="modal-header border-secondary">
        <h5 class="modal-title fw-bold"><i class="fa-solid fa-robot text-primary me-2"></i>إضافة بوت جديد للاستضافة</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form action="/add_bot" method="POST">
        <div class="modal-body p-4">
          <div class="mb-3">
            <label class="form-label">اسم البوت</label>
            <input type="text" name="name" class="form-control bg-secondary text-white border-0 py-2" placeholder="مثال: Nexus Bot" required>
          </div>
          <div class="mb-3">
            <label class="form-label">توكن البوت (Bot Token)</label>
            <input type="password" name="token" class="form-control bg-secondary text-white border-0 py-2" placeholder="أدخل التوكن السري" required>
          </div>
          <div class="mb-3">
            <label class="form-label">بادئة الأوامر (Prefix)</label>
            <input type="text" name="prefix" value="!" class="form-control bg-secondary text-white border-0 py-2">
          </div>
          <div class="mb-2">
            <label class="form-label">لغة البرمجة (Runtime)</label>
            <select name="lang" class="form-select bg-secondary text-white border-0 py-2">
              <option value="Python">Python</option>
              <option value="JavaScript (Node.js)">JavaScript (Node.js)</option>
              <option value="Lua">Lua</option>
              <option value="TypeScript">TypeScript</option>
            </select>
          </div>
        </div>
        <div class="modal-footer border-secondary p-3">
          <button type="button" class="btn btn-outline-danger px-4" data-bs-dismiss="modal"><i class="fa-solid fa-xmark me-1"></i> عدم حفظ</button>
          <button type="submit" class="btn btn-success px-4 fw-bold"><i class="fa-solid fa-check me-1"></i> حفظ</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function switchTab(tabId, btn) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('d-none'));
  document.querySelectorAll('.tab-trigger').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.remove('d-none');
  btn.classList.add('active');
}
const term = document.getElementById('terminalLogs');
if(term) term.scrollTop = term.scrollHeight;
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
    ai_diagnosis = "لم يتم رصد أي أخطاء حرجة في السجلات الحالية."
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
    add_bot_log(new_bot_idx, f"تم إنشاء البوت وإضافته بنجاح ضمن بيئة ({bot_lang}).")
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
            add_bot_log(bot_idx, f"▶️ تم تشغيل البوت ({bot['name']}) بنجاح واستقرار.")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(bot_idx, f"⏹️ تم إيقاف تشغيل البوت ({bot['name']}).")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(bot_idx, f"🔄 جاري إعادة تشغيل البوت ({bot['name']})... النظام يعمل بكفاءة.")
        
        save_data(BOTS_FILE, all_bots)

    return redirect(url_for('index', bot=bot_idx))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
