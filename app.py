"""
===================================================================
 NEXUS STORE • Ultimate Discord Bot Hosting & AI Diagnostics Manager
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
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

# ==================== إعدادات تطبيق ديسكورد OAuth2 ====================
CLIENT_ID = "1557517949001007104"
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://nexus-store-6ktz.onrender.com/callback")

DISCORD_API_BASE = "https://discord.com/api/v10"
OAUTH2_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20email%20guilds"

# ضع آيدي ديسكورد الخاص بك هنا ليكون مديراً عاماً (Admin) للوحة
ADMIN_DISCORD_IDS = ["ضع_ايدي_الديسكورد_الخاص_بك_هنا"]

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

def add_bot_log(user_id, bot_idx, message):
    logs = load_data(LOGS_FILE)
    key = f"{user_id}_{bot_idx}"
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
        return f"التوكن الخاص بـ ({bot_name}) برمجة ({lang}) غير صحيح أو منتهي. تحقق من إعدادات التوكن."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"البوت يفتقد لصلاحيات الـ Intents في Discord Developer Portal (فعّل Message Content و Server Members)."
    elif "modulenotfound" in log_lower or "cannot find module" in log_lower:
        return f"توجد مكتبة برمجية ناقصة لم يتم تثبيتها للغة ({lang}). تحقق من ملف المتطلبات."
    else:
        return f"البوت ({bot_name}) بلغة ({lang}) يعمل بشكل مستقر ولا توجد أخطاء حرجة."

# ==================== تصميم الواجهة (HTML Template) ====================
BASE_CSS = """
:root{--ink:#0e1322;--rack:#151b30;--rack2:#1b2340;--line:#2a3354;--text:#e9edf9;--muted:#94a0c2;--accent:#8b93ff;--accent-ink:#0e1322;--on:#3ddbb0;--off:#ff7a8a;--gold:#f3bd45}
*{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--text);font-family:'IBM Plex Sans Arabic',Tahoma,sans-serif;min-height:100vh;line-height:1.7}
a{text-decoration:none}
.muted{color:var(--muted)!important}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.shell{max-width:1320px;margin:auto;padding:20px 24px 28px}
.btn{border-radius:8px;font-weight:600;padding:8px 14px;font-size:14px}
.btn-sm{padding:6px 11px;font-size:13px}
.btn-primary-x{background:var(--accent);color:var(--accent-ink);border:1px solid var(--accent)}
.btn-primary-x:hover{background:#a3a9ff;color:var(--accent-ink)}
.btn-discord{background:#5865f2;color:#fff;border:0}.btn-discord:hover{background:#4752c4;color:#fff}
.btn-quiet{background:transparent;border:1px solid var(--line);color:var(--text)}
.btn-quiet:hover{background:var(--rack2);color:#fff}
.lamp{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--off);box-shadow:0 0 0 3px #ff7a8a22;flex:0 0 9px}
.lamp.on{background:var(--on);box-shadow:0 0 0 3px #3ddbb022,0 0 10px #3ddbb099;animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{50%{box-shadow:0 0 0 3px #3ddbb022,0 0 3px #3ddbb055}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.form-select,.form-control{background-color:#0b101d!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:8px!important}
.form-select:focus,.form-control:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px #8b93ff25!important}
.form-control::placeholder{color:#6f7a9b}
"""

HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus Hosting — لوحة التحكم</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<style>
{{ base_css|safe }}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding-bottom:18px;border-bottom:1px solid var(--line);margin-bottom:22px}
.brand{display:flex;align-items:center;gap:12px;color:var(--text)}
.brand-mark{width:40px;height:40px;border-radius:10px;display:grid;place-items:center;background:var(--accent);color:var(--accent-ink);font-size:17px}
.brand b{display:block;font-size:17px;font-weight:700;line-height:1.2}
.brand small{color:var(--muted);font-size:12px}
.user-pill{display:flex;align-items:center;gap:10px;padding:5px 6px 5px 12px;border:1px solid var(--line);border-radius:10px;background:var(--rack)}
.avatar-img{width:34px;height:34px;border-radius:8px;object-fit:cover}
.page-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-bottom:16px}
.page-head h2{font-size:26px;font-weight:700;margin:0}
.page-head p{margin:2px 0 0;color:var(--muted);font-size:14px}
.strip{display:flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:12px;background:var(--rack);margin-bottom:20px}
.strip>div{flex:1 1 160px;padding:12px 18px;border-inline-start:1px solid var(--line)}
.strip>div:first-child{border-inline-start:0}
.strip span{display:block;font-size:12px;color:var(--muted)}
.strip b{font-size:17px;font-weight:600}
.layout{display:grid;grid-template-columns:300px minmax(0,1fr);gap:20px;align-items:start}
@media(max-width:900px){.layout{grid-template-columns:1fr}.shell{padding:16px}}
.rack{border:1px solid var(--line);border-radius:12px;background:var(--rack);overflow:hidden}
.rack-head{display:flex;justify-content:space-between;align-items:center;padding:13px 16px;border-bottom:1px solid var(--line);font-weight:600;font-size:14px}
.rack-head span{font-weight:400;color:var(--muted);font-size:12px}
.unit{display:flex;align-items:center;gap:12px;padding:13px 16px;color:var(--text);border-bottom:1px solid var(--line);border-inline-start:3px solid transparent;transition:background .15s}
.unit:last-child{border-bottom:0}
.unit:hover{background:var(--rack2);color:#fff}
.unit.active{background:var(--rack2);border-inline-start-color:var(--accent)}
.unit-name{font-weight:600;font-size:14px;line-height:1.3}
.unit-meta{font-size:12px;color:var(--muted)}
.rack-empty{padding:28px 16px;text-align:center;color:var(--muted);font-size:14px}
.stage{border:1px solid var(--line);border-radius:12px;background:var(--rack);overflow:hidden}
.stage-head{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;padding:16px 20px;border-bottom:1px solid var(--line)}
.stage-head h3{font-size:20px;font-weight:700;margin:0;display:flex;align-items:center;gap:10px}
.state{font-size:13px;color:var(--muted);font-weight:500}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.seg a{padding:7px 14px;font-size:13px;font-weight:600;color:var(--text);border-inline-start:1px solid var(--line)}
.seg a:first-child{border-inline-start:0}
.seg a:hover{background:var(--rack2);color:#fff}
.seg .go{color:var(--on)}.seg .halt{color:var(--off)}
.meta-row{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center;padding:14px 20px;border-bottom:1px solid var(--line);font-size:14px}
.meta-row dt{display:inline;color:var(--muted);font-weight:400;margin-inline-end:6px}
.meta-row dd{display:inline;margin:0;font-weight:500}
.meta-row form{margin-inline-start:auto;display:flex;gap:8px;align-items:center}
.meta-row .form-select{width:auto;min-width:170px}
.console{padding:18px 20px}
.console h4{font-size:14px;font-weight:600;margin:0 0 10px;color:var(--muted)}
.console-box{direction:ltr;text-align:left;background:#080c17;color:#9be8c9;font:12.5px/1.9 'JetBrains Mono',ui-monospace,Consolas,monospace;border:1px solid var(--line);border-radius:10px;padding:16px;height:min(46vh,380px);overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}
.diag{margin:0 20px 20px;padding:12px 16px;border-inline-start:3px solid var(--gold);background:#1d1e2a;border-radius:6px}
.diag b{display:block;font-size:14px;margin-bottom:2px}
.diag p{margin:0;font-size:14px;color:#d8dcec}
.diag small{display:block;margin-top:6px;color:var(--muted);font-size:12px}
.hello{max-width:640px;margin:70px auto;text-align:center;padding:0 12px}
.hello .brand-mark{width:60px;height:60px;border-radius:16px;font-size:26px;margin:0 auto 20px}
.hello h2{font-size:30px;font-weight:700;margin-bottom:10px}
.hello p{color:var(--muted);margin:0 auto 24px;max-width:520px}
.admin-banner{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;padding:11px 16px;margin-bottom:18px;border:1px solid #f3bd4560;border-radius:10px;background:#2a2312;color:var(--gold);font-size:14px}
footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);text-align:center;color:#6f7a9b;font-size:12px}
.modal-content{background:var(--rack)!important;border:1px solid var(--line)!important;border-radius:14px!important}
.modal-header,.modal-footer{border-color:var(--line)!important}
.form-label{font-size:13px;color:#c9d1ea}
.btn-close-white{filter:invert(1)}
</style>
</head>
<body>
<div class="shell">
<header class="topbar">
  <a class="brand" href="/">
    <span class="brand-mark"><i class="fa-solid fa-cubes-stacked"></i></span>
    <span><b>Nexus Hosting</b><small>استضافة بوتات ديسكورد</small></span>
  </a>
  <div class="d-flex align-items-center gap-2">
    {% if is_admin %}
    <a href="/admin" class="btn btn-sm btn-quiet" style="color:var(--gold);border-color:#f3bd4560"><i class="fa-solid fa-shield-halved ms-1"></i> لوحة الأدمن</a>
    {% endif %}
    {% if user %}
    <div class="user-pill">
      <div style="line-height:1.3"><div style="font-weight:600;font-size:13px">{{ user.username }}</div><small class="muted">متصل عبر Discord</small></div>
      <img src="{{ user.avatar_url }}" class="avatar-img" alt="">
      <a href="/logout" class="btn btn-quiet btn-sm" title="تسجيل الخروج" aria-label="تسجيل الخروج"><i class="fa-solid fa-arrow-right-from-bracket"></i></a>
    </div>
    {% else %}
    <a href="/login" class="btn btn-discord"><i class="fa-brands fa-discord ms-2"></i> تسجيل الدخول عبر Discord</a>
    {% endif %}
  </div>
</header>

{% if admin_viewing %}
<div class="admin-banner">
  <div><i class="fa-solid fa-eye ms-2"></i>وضع الإدارة: تتصفح الآن بوتات المستخدم <code>{{ viewing_user_id }}</code></div>
  <a href="/" class="btn btn-sm btn-quiet">العودة للوحتي</a>
</div>
{% endif %}

{% if user %}
<section class="page-head">
  <div><h2>بوتاتي</h2><p>شغّل بوتاتك، تابع السجلات، وعدّل الإعدادات من مكان واحد.</p></div>
  <button class="btn btn-primary-x" data-bs-toggle="modal" data-bs-target="#addBotModal"><i class="fa-solid fa-plus ms-2"></i>إضافة بوت</button>
</section>
<div class="strip">
  <div><span>عدد البوتات</span><b>{{ user_bots|length }}</b></div>
  <div><span>حالة البوت المحدد</span><b>{% if active_bot %}{{ active_bot.status }}{% else %}—{% endif %}</b></div>
  <div><span>لغة البوت المحدد</span><b>{% if active_bot %}{{ active_bot.lang }}{% else %}—{% endif %}</b></div>
</div>
<div class="layout">
  <aside class="rack">
    <div class="rack-head">قائمة البوتات<span>{{ user_bots|length }}</span></div>
    {% for bot in user_bots %}
      <a href="/?{% if admin_viewing %}view_user={{ viewing_user_id }}&{% endif %}bot={{ loop.index0 }}" class="unit {% if selected_bot_idx == loop.index0 %}active{% endif %}">
        <span class="lamp {% if bot.status == 'شغال' %}on{% endif %}" title="{{ bot.status }}"></span>
        <span><div class="unit-name">{{ bot.name }}</div><div class="unit-meta">{{ bot.lang }} — البادئة {{ bot.prefix }}</div></span>
      </a>
    {% else %}
      <div class="rack-empty">لا توجد بوتات بعد.<br>اضغط «إضافة بوت» للبدء.</div>
    {% endfor %}
  </aside>
  <main>
    {% if active_bot %}
    <section class="stage">
      <div class="stage-head">
        <h3><span class="lamp {% if active_bot.status == 'شغال' %}on{% endif %}"></span>{{ active_bot.name }}<span class="state">{{ active_bot.status }}</span></h3>
        <div class="seg">
          <a class="go" href="/bot_action/{{ selected_bot_idx }}/start{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}"><i class="fa-solid fa-play ms-1"></i> تشغيل</a>
          <a class="halt" href="/bot_action/{{ selected_bot_idx }}/stop{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}"><i class="fa-solid fa-stop ms-1"></i> إيقاف</a>
          <a href="/bot_action/{{ selected_bot_idx }}/restart{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}"><i class="fa-solid fa-rotate ms-1"></i> إعادة تشغيل</a>
        </div>
      </div>
      <dl class="meta-row mb-0">
        <div><dt>بادئة الأوامر</dt><dd><code>{{ active_bot.prefix }}</code></dd></div>
        <div><dt>لغة البرمجة</dt><dd>{{ active_bot.lang }}</dd></div>
        <form action="/update_lang/{{ selected_bot_idx }}{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}" method="POST">
          <select name="lang" class="form-select form-select-sm" aria-label="لغة البرمجة">
            <option value="Python" {% if active_bot.lang == 'Python' %}selected{% endif %}>Python</option>
            <option value="JavaScript (Node.js)" {% if active_bot.lang == 'JavaScript (Node.js)' %}selected{% endif %}>JavaScript (Node.js)</option>
            <option value="Lua" {% if active_bot.lang == 'Lua' %}selected{% endif %}>Lua</option>
            <option value="TypeScript" {% if active_bot.lang == 'TypeScript' %}selected{% endif %}>TypeScript</option>
          </select>
          <button class="btn btn-quiet btn-sm" type="submit">حفظ اللغة</button>
        </form>
      </dl>
      <div class="console">
        <h4>سجل العمليات</h4>
        <div class="console-box" id="consoleLogs">{% for log in bot_logs %}{{ log }}
{% else %}لا توجد أحداث بعد. ستظهر هنا عمليات التشغيل والإيقاف والتعديل.
{% endfor %}</div>
      </div>
      <div class="diag">
        <b>تشخيص الأخطاء</b>
        <p>{{ ai_diagnosis }}</p>
        <small>تحليل مبسّط من السجلات المحفوظة، وليس فحصًا مباشرًا لعملية البوت.</small>
      </div>
    </section>
    {% else %}
    <section class="stage"><div class="hello" style="margin:48px auto">
      <h2 style="font-size:22px">اختر بوتًا أو أضف بوتًا جديدًا</h2>
      <p>بعد إضافة أول بوت ستظهر هنا أزرار التحكم والسجلات.</p>
      <button class="btn btn-primary-x" data-bs-toggle="modal" data-bs-target="#addBotModal"><i class="fa-solid fa-plus ms-2"></i>إضافة أول بوت</button>
    </div></section>
    {% endif %}
  </main>
</div>
{% else %}
<section class="hello">
  <div class="brand-mark"><i class="fa-solid fa-cubes-stacked"></i></div>
  <h2>شغّل بوتات ديسكورد من لوحة واحدة</h2>
  <p>أضف بوتك، شغّله، وتابع سجلاته مباشرة. سجّل الدخول بحساب ديسكورد للبدء.</p>
  <a href="/login" class="btn btn-discord btn-lg"><i class="fa-brands fa-discord ms-2"></i>تسجيل الدخول عبر Discord</a>
</section>
{% endif %}

<footer>© 2026 Nexus Hosting — جميع الحقوق محفوظة</footer>
</div>
{% if user %}
<div class="modal fade" id="addBotModal" tabindex="-1" aria-hidden="true"><div class="modal-dialog modal-dialog-centered"><div class="modal-content text-white">
  <div class="modal-header"><h5 class="modal-title fw-bold">إضافة بوت</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="إغلاق"></button></div>
  <form action="/add_bot" method="POST"><div class="modal-body">
    <div class="mb-3"><label class="form-label">اسم البوت</label><input type="text" name="name" class="form-control" placeholder="مثال: Nexus Support" required maxlength="80"></div>
    <div class="mb-3"><label class="form-label">توكن البوت</label><input type="password" name="token" class="form-control" placeholder="الصق التوكن هنا" required autocomplete="new-password"><div class="form-text text-secondary">لا تشارك التوكن مع أي شخص.</div></div>
    <div class="mb-3"><label class="form-label">بادئة الأوامر</label><input type="text" name="prefix" value="!" class="form-control" maxlength="10"></div>
    <div class="mb-2"><label class="form-label">لغة البرمجة</label><select name="lang" class="form-select"><option value="Python">Python</option><option value="JavaScript (Node.js)">JavaScript (Node.js)</option><option value="Lua">Lua</option><option value="TypeScript">TypeScript</option></select></div>
  </div><div class="modal-footer"><button type="button" class="btn btn-quiet" data-bs-dismiss="modal">إلغاء</button><button type="submit" class="btn btn-primary-x">إضافة البوت</button></div></form>
</div></div></div>
{% endif %}
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
const logs=document.getElementById('consoleLogs');if(logs)logs.scrollTop=logs.scrollHeight;
</script>
</body></html>
"""

# ==================== صفحات لوحة الأدمن (Admin Panel Template) ====================
ADMIN_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus Hosting — لوحة الأدمن</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
<style>
{{ base_css|safe }}
.wrap{max-width:1000px;margin:auto;padding:28px 20px}
.head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:20px}
.head h2{font-size:24px;font-weight:700;margin:0}
.panel-x{border:1px solid var(--line);border-radius:12px;background:var(--rack);overflow:hidden}
.panel-x h4{font-size:15px;font-weight:600;margin:0;padding:14px 18px;border-bottom:1px solid var(--line)}
.table{--bs-table-bg:transparent;--bs-table-color:var(--text);margin:0}
.table th{color:var(--muted);font-weight:500;font-size:13px;border-bottom:1px solid var(--line);padding:12px 18px}
.table td{border-bottom:1px solid var(--line);vertical-align:middle;padding:12px 18px;font-size:14px}
.table tr:last-child td{border-bottom:0}
.table-wrap{overflow-x:auto}
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h2><i class="fa-solid fa-shield-halved ms-2" style="color:var(--gold)"></i>لوحة الأدمن</h2>
    <a href="/" class="btn btn-quiet btn-sm">العودة للرئيسية</a>
  </div>
  <div class="panel-x">
    <h4>المستخدمون وبوتاتهم</h4>
    <div class="table-wrap">
    <table class="table">
      <thead>
        <tr><th>المعرّف (ID)</th><th>اسم المستخدم</th><th>عدد البوتات</th><th></th></tr>
      </thead>
      <tbody>
        {% for uid, bots in all_bots_data.items() %}
        <tr>
          <td><code>{{ uid }}</code></td>
          <td>{{ users_map.get(uid, {}).get('username', 'مستخدم غير معروف') }}</td>
          <td>{{ bots|length }}</td>
          <td class="text-start"><a href="/admin/view_user/{{ uid }}" class="btn btn-sm btn-quiet"><i class="fa-solid fa-eye ms-1"></i> تصفح البوتات</a></td>
        </tr>
        {% else %}
        <tr><td colspan="4" class="text-center muted py-4">لا يوجد مستخدمون أو بوتات مسجلة حتى الآن.</td></tr>
        {% endfor %}
      </tbody>
    </table>
    </div>
  </div>
</div>
</body>
</html>
"""

# ==================== المسارات والمنطق (Routes) ====================

@app.route('/')
def index():
    user = session.get('user')
    user_bots = []
    active_bot = None
    bot_logs = []
    ai_diagnosis = "لم يتم رصد أخطاء."
    
    is_admin = user and (user['id'] in ADMIN_DISCORD_IDS)
    
    # ميزة الأدمن: تصفح بوتات مستخدم آخر عبر ?view_user=USER_ID
    target_user_id = request.args.get('view_user')
    admin_viewing = False
    
    if is_admin and target_user_id:
        viewing_user_id = target_user_id
        admin_viewing = True
    elif user:
        viewing_user_id = user['id']
    else:
        viewing_user_id = None

    selected_bot_idx = request.args.get('bot', type=int)

    if viewing_user_id:
        all_bots = load_data(BOTS_FILE)
        user_bots = all_bots.get(viewing_user_id, [])
        
        if user_bots:
            if selected_bot_idx is None or selected_bot_idx >= len(user_bots):
                selected_bot_idx = 0
            active_bot = user_bots[selected_bot_idx]
            
            all_logs = load_data(LOGS_FILE)
            bot_logs = all_logs.get(f"{viewing_user_id}_{selected_bot_idx}", [])
            
            combined_logs = "\n".join(bot_logs)
            ai_diagnosis = ai_diagnose_issue(combined_logs, active_bot['name'], active_bot['lang'])

    return render_template_string(
        HTML_TEMPLATE,
        base_css=BASE_CSS,
        user=user, 
        user_bots=user_bots, 
        active_bot=active_bot, 
        selected_bot_idx=selected_bot_idx,
        bot_logs=bot_logs,
        ai_diagnosis=ai_diagnosis,
        is_admin=is_admin,
        admin_viewing=admin_viewing,
        viewing_user_id=viewing_user_id
    )

@app.route('/admin')
def admin_panel():
    user = session.get('user')
    if not user or user['id'] not in ADMIN_DISCORD_IDS:
        return "غير مأذون لك بالدخول إلى لوحة الأدمن.", 403
    
    all_bots_data = load_data(BOTS_FILE)
    users_map = load_data(USERS_FILE)
    
    return render_template_string(ADMIN_TEMPLATE, base_css=BASE_CSS, all_bots_data=all_bots_data, users_map=users_map)

@app.route('/admin/view_user/<uid>')
def admin_view_user(uid):
    user = session.get('user')
    if not user or user['id'] not in ADMIN_DISCORD_IDS:
        return "غير مأذون لك.", 403
    return redirect(url_for('index', view_user=uid))

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
    add_bot_log(user['id'], new_bot_idx, f"تم إضافة البوت بنجاح بلغة البرمجة ({bot_lang}).")
    return redirect(url_for('index', bot=new_bot_idx))

@app.route('/bot_action/<int:bot_idx>/<action>')
def bot_action(bot_idx, action):
    user = session.get('user')
    if not user or user['id'] not in ADMIN_DISCORD_IDS:
        # المستخدم العادي يتحكم ببوتاته فقط
        target_user_id = user['id'] if user else None
    else:
        # الأدمن يمكنه التحكم ببوت المستخدم الذي يتصفحه حالياً
        target_user_id = request.args.get('view_user') or user['id']

    if not target_user_id:
        return redirect(url_for('login'))

    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(target_user_id, [])

    if bot_idx < len(user_bots):
        bot = user_bots[bot_idx]
        if action == 'start':
            bot['status'] = 'شغال'
            add_bot_log(target_user_id, bot_idx, f"▶️ تم بدء تشغيل بوت ({bot['name']}) بنجاح.")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(target_user_id, bot_idx, f"⏹️ تم إيقاف تشغيل بوت ({bot['name']}).")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(target_user_id, bot_idx, f"🔄 جاري إعادة تشغيل بوت ({bot['name']})... البوت يعمل الآن.")
        
        save_data(BOTS_FILE, all_bots)

    redirect_url = url_for('index', bot=bot_idx)
    if target_user_id != user['id']:
        redirect_url += f"&view_user={target_user_id}"
    return redirect(redirect_url)

@app.route('/update_lang/<int:bot_idx>', methods=['POST'])
def update_lang(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
        
    target_user_id = request.args.get('view_user') if (user['id'] in ADMIN_DISCORD_IDS) else user['id']
    target_user_id = target_user_id or user['id']

    new_lang = request.form.get('lang', 'Python')
    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(target_user_id, [])

    if bot_idx < len(user_bots):
        user_bots[bot_idx]['lang'] = new_lang
        save_data(BOTS_FILE, all_bots)
        add_bot_log(target_user_id, bot_idx, f"💻 تم تغيير لغة برمجة البوت إلى: {new_lang}")

    redirect_url = url_for('index', bot=bot_idx)
    if target_user_id != user['id']:
        redirect_url += f"&view_user={target_user_id}"
    return redirect(redirect_url)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
