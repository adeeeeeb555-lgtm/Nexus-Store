"""
===================================================================
 NEXUS CLOUD HOSTING • Enterprise Discord Bot Platform
 Rights & Copyrights © Nexus Store - All Rights Reserved
===================================================================
"""
import os
import json
import time
import requests
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, session

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

MAX_BOTS_PER_USER = 3  # الحد الأقصى للبوتات لكل مستخدم في الخطة الحالية

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

def ai_diagnose_issue(log_text, bot_name, lang):
    log_lower = (log_text or "").lower()
    if "loginfailure" in log_lower or "token" in log_lower or "unauthorized" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي:** التوكن الخاص بـ ({bot_name}) غير صحيح أو منتهي الصلاحية. يرجى تعديله من إعدادات البوت."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي:** البوت يفتقر لصلاحيات الـ Intents في Discord Developer Portal."
    else:
        return f"✅ **تحليل الذكاء الاصطناعي:** البوت ({bot_name}) بلغة ({lang}) يعمل بشكل استثنائي ومستقر."

# ==================== تصميم الواجهة الشامل (HTML & CSS) ====================
HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus Cloud — لوحة إدارة البوتات</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<style>
:root {
  --bg-deep: #070a0f;
  --panel-bg: #0d121c;
  --panel-border: #1a2333;
  --gold-accent: #f3bd45;
  --text-main: #f3f4f6;
  --text-muted: #8b949e;
  --neon-green: #35c98a;
  --neon-red: #ff6b78;
  --active-blue: #38bdf8;
}

body {
  margin: 0; background-color: var(--bg-deep); color: var(--text-main);
  font-family: 'IBM Plex Sans Arabic', sans-serif; min-height: 100vh;
}
a { text-decoration: none; color: inherit; }
.shell { max-width: 1500px; margin: auto; padding: 24px; }

/* Navbar */
.navbar-nexus {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 24px; background: var(--panel-bg); border: 1px solid var(--panel-border);
  border-radius: 14px; margin-bottom: 25px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon { width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, #ffe18a, var(--gold-accent)); display: grid; place-items: center; color: #111; font-size: 20px; font-weight: bold; }

.btn-discord-main { background: #5865F2; color: white; padding: 12px 30px; border-radius: 12px; font-weight: 800; font-size: 18px; border: none; }
.btn-discord-main:hover { background: #4752c4; color: white; }

/* Resource Usage Bar Panel */
.resource-header-panel {
  background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 14px; padding: 20px; margin-bottom: 25px;
}
.resource-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.resource-item { border-left: 1px solid var(--panel-border); padding-left: 15px; }
.resource-item:last-child { border-left: none; }
.resource-item small { color: var(--text-muted); display: block; margin-bottom: 5px; }
.resource-item .val { font-size: 18px; font-weight: 800; }
.progress-bar-custom { height: 6px; background: #212d40; border-radius: 10px; margin-top: 8px; position: relative; overflow: hidden; }
.progress-bar-fill { height: 100%; background: var(--gold-accent); border-radius: 10px; }

/* Deployments Table */
.deployments-panel { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 14px; padding: 20px; }
.deploy-table { width: 100%; border-collapse: collapse; }
.deploy-table th { color: var(--text-muted); font-size: 13px; padding: 12px; border-bottom: 1px solid var(--panel-border); text-align: right; }
.deploy-table td { padding: 16px 12px; border-bottom: 1px solid #131a26; vertical-align: middle; }
.deploy-table tr:hover { background: rgba(255,255,255,0.01); cursor: pointer; }
.status-badge { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; }
.status-badge.on { background: rgba(53, 201, 138, 0.15); color: var(--neon-green); }
.status-badge.off { background: rgba(255, 107, 120, 0.15); color: var(--neon-red); }

/* Top Resource Bar in Bot Control */
.top-stats-bar {
  background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 14px;
  padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px;
}
.stat-box { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-muted); }
.stat-box strong { color: var(--text-main); font-size: 15px; }

/* Tabs */
.nav-tabs-nexus {
  display: flex; gap: 20px; border-bottom: 1px solid var(--panel-border); margin-bottom: 20px; padding-bottom: 8px; overflow-x: auto;
}
.nav-tab-item {
  color: var(--text-muted); font-size: 15px; font-weight: 700; padding: 8px 12px; cursor: pointer; position: relative; border: none; background: none;
}
.nav-tab-item:hover { color: var(--text-main); }
.nav-tab-item.active { color: var(--text-main); }
.nav-tab-item.active::after {
  content: ''; position: absolute; bottom: -9px; left: 0; width: 100%; height: 3px; background: white; border-radius: 2px;
}

/* Console Screen */
.console-box {
  background: #040609; color: var(--neon-green); font-family: monospace;
  padding: 20px; border-radius: 12px; border: 1px solid var(--panel-border);
  height: 380px; overflow-y: auto; font-size: 13.5px; line-height: 1.7; direction: ltr; text-align: left;
}

footer { border-top: 1px solid var(--panel-border); margin-top: 40px; padding: 20px 0; text-align: center; color: var(--text-muted); font-size: 12px; }
</style>
</head>
<body>
<div class="shell">

<!-- Navbar -->
<header class="navbar-nexus">
  <a href="/" class="brand">
    <div class="brand-icon"><i class="fa-solid fa-cubes"></i></div>
    <div>
      <h5 class="fw-bold m-0">NEXUS CLOUD</h5>
      <small style="color:var(--text-muted)">Discord Bot Hosting Platform</small>
    </div>
  </a>
  {% if user %}
  <div class="d-flex align-items-center gap-3">
    <div class="d-flex align-items-center gap-2 bg-dark px-3 py-1.5 rounded-pill border border-secondary">
      <img src="{{ user.avatar_url }}" width="32" height="32" class="rounded-circle">
      <span class="fw-bold fs-6">{{ user.username }}</span>
    </div>
    <a href="/logout" class="btn btn-outline-danger btn-sm"><i class="fa-solid fa-power-off"></i></a>
  </div>
  {% else %}
  <a href="/login" class="btn btn-discord-main"><i class="fa-brands fa-discord me-2"></i>تسجيل الدخول</a>
  {% endif %}
</header>

{% if not user %}
<div class="text-center py-5">
  <h1 class="fw-bold">استضافة بوتات ديسكورد الاحترافية والأسرع</h1>
  <p class="text-muted col-md-7 mx-auto mb-4">تحكم كامل ببوتاتك، مراقبة حية للموارد، ووحدة تحكم متكاملة.</p>
  <a href="/login" class="btn-discord-main"><i class="fa-brands fa-discord me-2"></i> ابدأ الآن عبر Discord</a>
</div>
{% else %}

{% if not active_bot %}
<!-- الصفحة الرئيسية -->
<div class="resource-header-panel">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h5 class="fw-bold m-0"><i class="fa-solid fa-chart-line text-warning me-2"></i>مجموعة الموارد</h5>
    <span class="text-warning fs-13 fw-bold">إدارة الخطة</span>
  </div>
  <div class="resource-grid">
    <div class="resource-item">
      <small>الذاكرة (RAM)</small>
      <div class="val">256 MB <span class="text-muted fs-6">من 512 MB</span></div>
      <div class="progress-bar-custom"><div class="progress-bar-fill" style="width: 50%;"></div></div>
    </div>
    <div class="resource-item">
      <small>CPU</small>
      <div class="val">15% <span class="text-muted fs-6">من 25%</span></div>
      <div class="progress-bar-custom"><div class="progress-bar-fill" style="width: 60%;"></div></div>
    </div>
    <div class="resource-item">
      <small>التخزين</small>
      <div class="val">210 MB <span class="text-muted fs-6">من 512 MB</span></div>
      <div class="progress-bar-custom"><div class="progress-bar-fill" style="width: 40%;"></div></div>
    </div>
    <div class="resource-item">
      <small>عمليات النشر</small>
      <div class="val">{{ user_bots|length }} <span class="text-muted fs-6">من {{ max_bots }}</span></div>
      <div class="progress-bar-custom"><div class="progress-bar-fill" style="width: {{ (user_bots|length / max_bots) * 100 }}%;"></div></div>
    </div>
  </div>
</div>

<div class="deployments-panel">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h5 class="fw-bold m-0">عمليات النشر (Deployments)</h5>
    <button class="btn btn-warning btn-sm fw-bold px-3" data-bs-toggle="modal" data-bs-target="#addBotModal">
      <i class="fa-solid fa-plus me-1"></i> نشر جديد
    </button>
  </div>
  
  <table class="deploy-table">
    <thead>
      <tr>
        <th>الاسم</th>
        <th>الحالة</th>
        <th>مدة التشغيل</th>
        <th>الذاكرة</th>
        <th>CPU</th>
        <th>التخزين</th>
        <th class="text-center">إدارة</th>
      </tr>
    </thead>
    <tbody>
      {% for bot in user_bots %}
      <tr>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">
          <div class="fw-bold text-white">{{ bot.name }}</div>
          <small class="text-muted"><i class="fa-solid fa-code me-1"></i>{{ bot.lang }}</small>
        </td>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">
          {% if bot.status == 'شغال' %}
          <span class="status-badge on"><i class="fa-solid fa-circle fs-8"></i> يعمل</span>
          {% else %}
          <span class="status-badge off"><i class="fa-solid fa-circle fs-8"></i> متوقف</span>
          {% endif %}
        </td>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">7 يوم</td>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">32 MB</td>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">0%</td>
        <td onclick="window.location.href='/?bot={{ loop.index0 }}'">45 MB</td>
        <td class="text-center">
          <a href="/delete_bot/{{ loop.index0 }}" class="btn btn-outline-danger btn-sm" onclick="return confirm('هل أنت متأكد من رغبتك في حذف هذا البوت نهائياً؟');" title="حذف البوت">
            <i class="fa-solid fa-trash"></i>
          </a>
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="7" class="text-center py-5 text-muted">لا توجد عمليات نشر حتى الآن. اضغط على "نشر جديد" لبدء بوتك الأول.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{% else %}
<!-- صفحة تحكم البوت الفردي المتقدمة -->
<div class="top-stats-bar">
  <div class="d-flex align-items-center gap-3">
    <a href="/" class="btn btn-outline-secondary btn-sm" title="العودة للمشاريع"><i class="fa-solid fa-arrow-right"></i></a>
    <h4 class="fw-bold m-0 text-white">{{ active_bot.name }}</h4>
    
    <form action="/update_lang/{{ selected_bot_idx }}" method="POST" class="d-flex align-items-center gap-1">
      <select name="lang" class="form-select form-select-sm bg-dark text-white border-secondary" style="width: auto;" onchange="this.form.submit()">
        <option value="Python" {% if active_bot.lang == 'Python' %}selected{% endif %}>Python</option>
        <option value="JavaScript (Node.js)" {% if active_bot.lang == 'JavaScript (Node.js)' %}selected{% endif %}>JavaScript (Node.js)</option>
        <option value="Lua" {% if active_bot.lang == 'Lua' %}selected{% endif %}>Lua</option>
        <option value="TypeScript" {% if active_bot.lang == 'TypeScript' %}selected{% endif %}>TypeScript</option>
      </select>
    </form>
  </div>

  <div class="d-flex align-items-center gap-4">
    <div class="stat-box">RAM: <strong>48 MB / 256 MB</strong></div>
    <div class="stat-box">CPU: <strong>0% / 15%</strong></div>
    <div class="stat-box">التخزين: <strong>59 MB / 512 MB</strong></div>
  </div>

  <div class="d-flex gap-2">
    <a href="/bot_action/{{ selected_bot_idx }}/start" class="btn btn-success btn-sm fw-bold px-3"><i class="fa-solid fa-play me-1"></i> تشغيل</a>
    <a href="/bot_action/{{ selected_bot_idx }}/stop" class="btn btn-danger btn-sm fw-bold px-3"><i class="fa-solid fa-stop me-1"></i> إيقاف</a>
    <a href="/bot_action/{{ selected_bot_idx }}/restart" class="btn btn-warning btn-sm fw-bold px-3 text-dark"><i class="fa-solid fa-rotate me-1"></i> إعادة تشغيل</a>
    <a href="/delete_bot/{{ selected_bot_idx }}" class="btn btn-outline-danger btn-sm px-3" onclick="return confirm('هل أنت متأكد من حذف هذا البوت؟');"><i class="fa-solid fa-trash"></i> حذف</a>
  </div>
</div>

<!-- شريط الخيارات -->
<div class="nav-tabs-nexus">
  <button class="nav-tab-item active" onclick="switchSection('consoleSection', this)">وحدة التحكم</button>
  <button class="nav-tab-item" onclick="switchSection('filesSection', this)">الملفات</button>
  <button class="nav-tab-item" onclick="switchSection('envSection', this)">البيئة & التوكن (.env)</button>
  <button class="nav-tab-item" onclick="switchSection('domainsSection', this)">النطاقات</button>
  <button class="nav-tab-item" onclick="switchSection('backupSection', this)">النسخ الاحتياطية</button>
</div>

<!-- 1. وحدة التحكم -->
<div id="consoleSection" class="section-pane">
  <div class="console-box" id="consoleLogs">{% for log in bot_logs %}{{ log }}
{% else %}[Nexus Engine] جاري تشغيل وحدة التحكم...
[Nexus Engine] الحاوية جاهزة وتعمل بلغة ({{ active_bot.lang }}).
{% endfor %}</div>

  <div class="mt-3 p-3 bg-secondary bg-opacity-10 rounded border border-warning">
    <h6 class="fw-bold text-warning mb-1"><i class="fa-solid fa-wand-magic-sparkles me-2"></i>تشخيص الذكاء الاصطناعي</h6>
    <p class="m-0 fs-6">{{ ai_diagnosis }}</p>
  </div>
</div>

<!-- 2. الملفات -->
<div id="filesSection" class="section-pane d-none">
  <div class="p-4 bg-dark rounded border border-secondary">
    <h6 class="fw-bold mb-3">مدير الملفات والمرئي</h6>
    <ul class="list-group list-group-flush bg-dark text-white">
      <li class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center">
        <span><i class="fa-solid fa-file-code text-warning me-2"></i> main.py</span>
        <span class="badge bg-secondary">جاهز</span>
      </li>
      <li class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center">
        <span><i class="fa-solid fa-file-lines text-info me-2"></i> requirements.txt</span>
        <span class="badge bg-secondary">جاهز</span>
      </li>
      <li class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center">
        <span><i class="fa-solid fa-lock text-danger me-2"></i> .env (مخفي وآمن)</span>
        <span class="badge bg-danger">محمي</span>
      </li>
    </ul>
  </div>
</div>

<!-- 3. البيئة وتغيير التوكن -->
<div id="envSection" class="section-pane d-none">
  <div class="p-4 bg-dark rounded border border-secondary">
    <h6 class="fw-bold mb-3"><i class="fa-solid fa-key text-warning me-2"></i>إدارة متغيرات البيئة وتوكن البوت</h6>
    <form action="/update_token/{{ selected_bot_idx }}" method="POST">
      <div class="mb-3">
        <label class="form-label text-muted">توكن البوت الحالي (Bot Token)</label>
        <div class="input-group">
          <input type="text" name="token" class="form-control bg-secondary text-white border-0" value="{{ active_bot.token }}" required>
          <button type="submit" class="btn btn-warning fw-bold">حفظ التوكن الجديد</button>
        </div>
        <small class="text-muted mt-2 d-block">تغيير التتوكن سيؤدي لإعادة تشغيل الحاوية وتطبيق الإعدادات الجديدة فوراً.</small>
      </div>
    </form>
  </div>
</div>

<!-- 4. النطاقات -->
<div id="domainsSection" class="section-pane d-none">
  <div class="p-4 bg-dark rounded border border-secondary text-center">
    <h6 class="fw-bold">إدارة النطاقات (Custom Domains)</h6>
    <p class="text-muted">ربط دومين مخصص ببوتك السحابي.</p>
  </div>
</div>

<!-- 5. النسخ الاحتياطية -->
<div id="backupSection" class="section-pane d-none">
  <div class="p-4 bg-dark rounded border border-secondary text-center">
    <h6 class="fw-bold">النسخ الاحتياطية (Backups)</h6>
    <p class="text-muted">حفظ نسخة احتياطية لكود وبيانات البوت بضغطة زر.</p>
  </div>
</div>

{% endif %}

{% endif %}

<footer>© 2026 Nexus Cloud Platform — جميع الحقوق محفوظة</footer>
</div>

<!-- Modal إضافة نشر جديد -->
{% if user %}
<div class="modal fade" id="addBotModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content bg-dark text-white border-secondary rounded-4">
      <div class="modal-header border-secondary">
        <h5 class="modal-title fw-bold">إنشاء عملية نشر جديدة</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form action="/add_bot" method="POST">
        <div class="modal-body p-4">
          <div class="mb-3">
            <label class="form-label">اسم البوت / المشروع</label>
            <input type="text" name="name" class="form-control bg-secondary text-white border-0" placeholder="مثال: Nexus Store" required>
          </div>
          <div class="mb-3">
            <label class="form-label">توكن البوت (Bot Token)</label>
            <input type="password" name="token" class="form-control bg-secondary text-white border-0" required>
          </div>
          <div class="mb-3">
            <label class="form-label">لغة البرمجة (Runtime)</label>
            <select name="lang" class="form-select bg-secondary text-white border-0">
              <option value="Python">Python</option>
              <option value="JavaScript (Node.js)">JavaScript (Node.js)</option>
              <option value="Lua">Lua</option>
              <option value="TypeScript">TypeScript</option>
            </select>
          </div>
        </div>
        <div class="modal-footer border-secondary">
          <button type="button" class="btn btn-outline-light" data-bs-dismiss="modal">إلغاء</button>
          <button type="submit" class="btn btn-warning fw-bold">بدء النشر</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function switchSection(sectionId, btn) {
  document.querySelectorAll('.section-pane').forEach(el => el.classList.add('d-none'));
  document.querySelectorAll('.nav-tab-item').forEach(el => el.classList.remove('active'));
  document.getElementById(sectionId).classList.remove('d-none');
  btn.classList.add('active');
}
const logs = document.getElementById('consoleLogs');
if(logs) logs.scrollTop = logs.scrollHeight;
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
    ai_diagnosis = "لم يتم رصد أي أخطاء."
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
        ai_diagnosis=ai_diagnosis,
        max_bots=MAX_BOTS_PER_USER
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
    bot_lang = request.form.get('lang', 'Python')

    all_bots = load_data(BOTS_FILE)
    if user['id'] not in all_bots:
        all_bots[user['id']] = []

    if len(all_bots[user['id']]) >= MAX_BOTS_PER_USER:
        return f"لقد وصلت للحد الأقصى المسموح به للبوتات ({MAX_BOTS_PER_USER} بوتات).", 400

    new_bot_idx = len(all_bots[user['id']])
    all_bots[user['id']].append({
        'name': bot_name,
        'token': bot_token,
        'lang': bot_lang,
        'status': 'شغال'
    })

    save_data(BOTS_FILE, all_bots)
    add_bot_log(new_bot_idx, f"تم نشر البوت بنجاح بلغة ({bot_lang}).")
    return redirect(url_for('index', bot=new_bot_idx))

@app.route('/delete_bot/<int:bot_idx>')
def delete_bot(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(user['id'], [])

    if 0 <= bot_idx < len(user_bots):
        deleted_bot = user_bots.pop(bot_idx)
        all_bots[user['id']] = user_bots
        save_data(BOTS_FILE, all_bots)

    return redirect(url_for('index'))

@app.route('/update_token/<int:bot_idx>', methods=['POST'])
def update_token(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    new_token = request.form.get('token')
    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(user['id'], [])

    if 0 <= bot_idx < len(user_bots):
        user_bots[bot_idx]['token'] = new_token
        save_data(BOTS_FILE, all_bots)
        add_bot_log(bot_idx, "🔑 تم تحديث توكن البوت بنجاح وإعادة تشغيل الحاوية.")

    return redirect(url_for('index', bot=bot_idx))

@app.route('/update_lang/<int:bot_idx>', methods=['POST'])
def update_lang(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    new_lang = request.form.get('lang', 'Python')
    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(user['id'], [])

    if bot_idx < len(user_bots):
        user_bots[bot_idx]['lang'] = new_lang
        save_data(BOTS_FILE, all_bots)
        add_bot_log(bot_idx, f"💻 تم تحديث وتغيير لغة البرمجة إلى: {new_lang}")

    return redirect(url_for('index', bot=bot_idx))

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
            add_bot_log(bot_idx, f"▶️ تم تشغيل البوت بنجاح.")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(bot_idx, f"⏹️ تم إيقاف الحاوية.")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(bot_idx, f"🔄 جاري إعادة تشغيل البوت...")
        
        save_data(BOTS_FILE, all_bots)

    return redirect(url_for('index', bot=bot_idx))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
