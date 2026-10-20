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
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

# ==================== إعدادات تطبيق ديسكورد OAuth2 ====================
CLIENT_ID = "1557517949001007104"
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://nexus-store-6ktz.onrender.com/callback")

DISCORD_API_BASE = "https://discord.com/api/v10"
OAUTH2_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20email%20guilds"

# آيدي الأدمن المخصص حصرياً
ADMIN_DISCORD_IDS = ["1374409912041603102"]

# ==================== قواعد البيانات المحلية ====================
BASE = Path(__file__).resolve().parent
USERS_FILE = BASE / "users_db.json"
BOTS_FILE = BASE / "user_bots.json"
LOGS_FILE = BASE / "bot_logs.json"
BOT_FILES_DIR = BASE / "bot_source_files"
BOT_FILES_DIR.mkdir(exist_ok=True)

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

def ai_diagnose_issue(log_text, bot_name, lang):
    log_lower = (log_text or "").lower()
    if "loginfailure" in log_lower or "token" in log_lower or "unauthorized" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** التوكن الخاص بـ ({bot_name}) برمجة ({lang}) غير صحيح أو منتهي."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** البوت يفتقد لصلاحيات الـ Intents في Discord Developer Portal."
    else:
        return f"✅ **تحليل الذكاء الاصطناعي (AI):** البوت ({bot_name}) بلغة ({lang}) يعمل بشكل مستقر."

# ==================== تصميم الواجهة (HTML Template) ====================
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
:root{--bg:#0b0e14;--panel:#111620;--line:#242d3b;--muted:#8c98aa;--text:#edf2f9;--gold:#f3bd45;--green:#35c98a;--red:#ff6b78}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 75% -10%,#1b2536 0,transparent 42%),var(--bg);color:var(--text);font-family:'IBM Plex Sans Arabic',Tahoma,sans-serif;min-height:100vh}
a{text-decoration:none}.shell{max-width:1440px;margin:auto;padding:24px}.topbar{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:12px 0 24px;border-bottom:1px solid var(--line);margin-bottom:26px}
.brand{display:flex;align-items:center;gap:13px}.brand-mark{width:45px;height:45px;border-radius:14px;display:grid;place-items:center;color:#111;background:linear-gradient(145deg,#ffe18a,var(--gold));font-size:20px}.brand h1{font-size:18px;font-weight:800;margin:0}.brand small{display:block;color:var(--muted);font-size:12px}
.user-pill{display:flex;align-items:center;gap:10px;background:#131a25;border:1px solid var(--line);border-radius:14px;padding:8px 12px}.avatar-img{width:38px;height:38px;border-radius:12px;border:1px solid #ffffff25;object-fit:cover}.muted{color:var(--muted)!important}.eyebrow{color:var(--gold);font-size:12px;font-weight:700}.hero{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:4px 0 26px}.hero h2{font-size:clamp(24px,3vw,34px);font-weight:800;margin:8px 0}.hero p{color:var(--muted);margin:0}.btn{border-radius:10px;font-weight:700;padding:10px 15px}.btn-nexus{background:var(--gold);color:#16130a;border:1px solid var(--gold)}.btn-discord{background:#5865f2;color:#fff;border:0}.btn-quiet{background:#171e2a;border:1px solid var(--line);color:var(--text)}.btn-sm{padding:7px 10px;font-size:12px}.layout{display:grid;grid-template-columns:310px minmax(0,1fr);gap:22px;align-items:start}.panel{background:linear-gradient(145deg,#131a25,#10151e);border:1px solid var(--line);border-radius:18px;padding:21px}.panel-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}.panel-head h3{font-size:16px;font-weight:800;margin:0}.count{font-size:12px;color:var(--muted);background:#1c2533;border-radius:8px;padding:5px 9px}.bot-list{display:grid;gap:10px}.bot-item{display:block;padding:14px;border-radius:13px;border:1px solid var(--line);background:#0f141d;color:var(--text);transition:.18s}.bot-item:hover{border-color:#687080;color:white}.bot-item.active{border-color:#c99b37;background:linear-gradient(110deg,#342b18,#171b22);box-shadow:inset -3px 0 var(--gold)}.bot-title{display:flex;justify-content:space-between;gap:8px;align-items:center;font-weight:700;font-size:14px}.bot-meta{font-size:12px;color:var(--muted);margin-top:9px}.status{font-size:11px;font-weight:700;border-radius:99px;padding:4px 8px}.status.on{background:#153b30;color:#60e2ad}.status.off{background:#392129;color:#ff929c}.empty{padding:30px 12px;text-align:center;border:1px dashed #303a4a;border-radius:13px;color:var(--muted)}.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-bottom:20px}.stat{padding:16px;border:1px solid var(--line);border-radius:15px;background:#111721}.stat-label{font-size:12px;color:var(--muted)}.stat-value{font-size:22px;font-weight:800;margin-top:8px}.stat-icon{float:left;color:var(--gold);font-size:16px}.control-title{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:20px}.control-title h3{font-size:20px;font-weight:800;margin:0}.details-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin-bottom:22px}.detail{background:#0e141d;border:1px solid var(--line);border-radius:14px;padding:17px}.detail h4{font-size:13px;font-weight:700;margin:0 0 14px}.detail p{font-size:13px;margin:9px 0;color:#dbe2ec}.form-select,.form-control{background-color:#0b1018!important;color:var(--text)!important;border:1px solid #2a3545!important;border-radius:10px!important}.console-box{direction:ltr;text-align:left;background:#080c12;color:#86e7b3;font:12px/1.9 monospace;border:1px solid #263140;border-radius:13px;padding:16px;height:220px;overflow:auto;white-space:pre-wrap}.ai-box{display:flex;gap:13px;align-items:flex-start;margin-top:16px;padding:16px;border:1px solid #51452b;background:#201d16;border-radius:14px}.ai-icon{width:38px;height:38px;flex:0 0 38px;border-radius:11px;background:#3a301b;color:var(--gold);display:grid;place-items:center}.welcome{max-width:760px;margin:70px auto;text-align:center;padding:55px 28px}.welcome-logo{width:76px;height:76px;border-radius:24px;margin:0 auto 22px;display:grid;place-items:center;background:#f3bd4517;border:1px solid #f3bd4540;color:var(--gold);font-size:31px}footer{margin-top:34px;padding:22px 0;border-top:1px solid var(--line);text-align:center;color:#748096;font-size:12px}.modal-content{background:#111721!important;border:1px solid var(--line)!important;border-radius:17px!important}.form-label{font-size:13px;color:#c7d0de}.btn-close-white{filter:invert(1)}.shortcut-tip{background:#151c28;border:1px dashed var(--gold);color:var(--gold);padding:8px 14px;border-radius:10px;font-size:13px;margin-bottom:15px;display:inline-block}
</style>
</head>
<body>
<div class="shell">
<header class="topbar">
  <a class="brand" href="/">
    <span class="brand-mark"><i class="fa-solid fa-cubes-stacked"></i></span>
    <span><h1>NEXUS HOSTING</h1><small>Discord Bot Control Center</small></span>
  </a>
  <div class="d-flex align-items-center gap-2">
    {% if is_admin %}
    <a href="/admin" class="btn btn-sm" style="background:#3a280b;color:var(--gold);border:1px solid #f3bd4550"><i class="fa-solid fa-shield-halved ms-1"></i> لوحة الأدمن</a>
    {% endif %}
    {% if user %}
    <div class="user-pill">
      <img src="{{ user.avatar_url }}" class="avatar-img" alt="Avatar">
      <div><div style="font-weight:700;font-size:13px">{{ user.username }}</div><small class="muted">حساب ديسكورد متصل</small></div>
      <a href="/logout" class="btn btn-quiet btn-sm me-1" title="تسجيل الخروج"><i class="fa-solid fa-arrow-right-from-bracket"></i></a>
    </div>
    {% else %}
    <a href="/login" class="btn btn-discord"><i class="fa-brands fa-discord ms-2"></i> تسجيل الدخول عبر Discord</a>
    {% endif %}
  </div>
</header>

<div class="shortcut-tip">
  <i class="fa-solid fa-keyboard ms-1"></i> <strong>اختصارات الكيبورد:</strong> اضغط <code>Ctrl + Shift + B</code> لفتح نافذة إدارة الملفات البرمجية | اضغط <code>F5</code> لتحديث الصفحة والسجلات.
</div>

{% if admin_viewing %}
<div class="alert alert-warning mb-4 d-flex justify-content-between align-items-center" style="background:#2a2211;border-color:#f3bd45;color:#f3bd45">
  <div><i class="fa-solid fa-triangle-exclamation ms-2"></i><strong>وضع الإدارة (Admin View):</strong> أنت تتصفح بوتات المستخدم: <code>{{ viewing_user_id }}</code></div>
  <a href="/" class="btn btn-sm btn-quiet" style="background:#111;color:#fff">العودة للوحة الخاصة بك</a>
</div>
{% endif %}

{% if user %}
<section class="hero">
  <div><div class="eyebrow">مساحة العمل / DASHBOARD</div><h2>أهلًا بك في لوحة التحكم</h2><p>تابع بوتاتك، راقب السجلات، وتحكّم بإعدادات الاستضافة من مكان واحد.</p></div>
  <div class="d-flex gap-2">
    <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#filesModal"><i class="fa-solid fa-folder-open ms-2"></i>ملفات البوت</button>
    <button class="btn btn-nexus" data-bs-toggle="modal" data-bs-target="#addBotModal"><i class="fa-solid fa-plus ms-2"></i>إضافة بوت جديد</button>
  </div>
</section>

<div class="stats">
  <div class="stat"><i class="fa-solid fa-robot stat-icon"></i><div class="stat-label">إجمالي البوتات</div><div class="stat-value">{{ user_bots|length }}</div></div>
  <div class="stat"><i class="fa-solid fa-circle-play stat-icon"></i><div class="stat-label">حالة البوت المحدد</div><div class="stat-value" style="font-size:18px">{% if active_bot %}{{ active_bot.status }}{% else %}—{% endif %}</div></div>
  <div class="stat"><i class="fa-solid fa-code stat-icon"></i><div class="stat-label">لغة البوت المحدد</div><div class="stat-value" style="font-size:18px">{% if active_bot %}{{ active_bot.lang }}{% else %}—{% endif %}</div></div>
</div>

<div class="layout">
  <aside class="panel">
    <div class="panel-head"><h3><i class="fa-solid fa-layer-group ms-2" style="color:var(--gold)"></i>بوتاتي</h3><span class="count">{{ user_bots|length }} بوت</span></div>
    <div class="bot-list">
    {% for bot in user_bots %}
      <a href="/?{% if admin_viewing %}view_user={{ viewing_user_id }}&{% endif %}bot={{ loop.index0 }}" class="bot-item {% if selected_bot_idx == loop.index0 %}active{% endif %}">
        <div class="bot-title"><span><i class="fa-solid fa-robot ms-2 muted"></i>{{ bot.name }}</span><span class="status {% if bot.status == 'شغال' %}on{% else %}off{% endif %}">{{ bot.status }}</span></div>
        <div class="bot-meta">{{ bot.lang }} • Prefix: {{ bot.prefix }}</div>
      </a>
    {% else %}
      <div class="empty"><i class="fa-solid fa-box-open d-block"></i><div style="color:#cbd4e2;font-weight:700;margin-bottom:5px">ما عندك بوتات حتى الآن</div><small>أضف أول بوت لك للبدء.</small></div>
    {% endfor %}
    </div>
  </aside>
  
  <main>
    {% if active_bot %}
    <section class="panel">
      <div class="control-title">
        <div><div class="eyebrow">BOT OVERVIEW</div><h3 class="mt-2">{{ active_bot.name }}</h3></div>
        <div class="action-row">
          <a href="/bot_action/{{ selected_bot_idx }}/start{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}" class="btn btn-sm" style="background:#174532;color:#70e4b1"><i class="fa-solid fa-play ms-1"></i> تشغيل</a>
          <a href="/bot_action/{{ selected_bot_idx }}/stop{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}" class="btn btn-sm" style="background:#45202a;color:#ff9ca5"><i class="fa-solid fa-stop ms-1"></i> إيقاف</a>
          <a href="/bot_action/{{ selected_bot_idx }}/restart{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}" class="btn btn-sm btn-quiet"><i class="fa-solid fa-rotate ms-1"></i> إعادة تشغيل</a>
        </div>
      </div>
      <div class="details-grid">
        <div class="detail"><h4><i class="fa-solid fa-circle-info ms-2" style="color:var(--gold)"></i>معلومات البوت</h4>
          <p><strong>الحالة</strong><span class="status {% if active_bot.status == 'شغال' %}on{% else %}off{% endif %}">{{ active_bot.status }}</span></p>
          <p><strong>بادئة الأوامر</strong><code style="color:var(--gold)">{{ active_bot.prefix }}</code></p>
          <p><strong>لغة البرمجة</strong>{{ active_bot.lang }}</p>
        </div>
        <div class="detail"><h4><i class="fa-solid fa-code ms-2" style="color:var(--gold)"></i>إعدادات التشغيل</h4>
          <form action="/update_lang/{{ selected_bot_idx }}{% if admin_viewing %}?view_user={{ viewing_user_id }}{% endif %}" method="POST">
            <label class="form-label">لغة البرمجة</label>
            <div class="d-flex gap-2"><select name="lang" class="form-select form-select-sm">
              <option value="Python" {% if active_bot.lang == 'Python' %}selected{% endif %}>Python</option>
              <option value="JavaScript (Node.js)" {% if active_bot.lang == 'JavaScript (Node.js)' %}selected{% endif %}>JavaScript (Node.js)</option>
              <option value="Lua" {% if active_bot.lang == 'Lua' %}selected{% endif %}>Lua</option>
              <option value="TypeScript" {% if active_bot.lang == 'TypeScript' %}selected{% endif %}>TypeScript</option>
            </select><button class="btn btn-nexus btn-sm" type="submit">حفظ</button></div>
          </form>
        </div>
      </div>
      <div class="console-head"><h4><i class="fa-solid fa-terminal ms-2" style="color:var(--gold)"></i>سجل العمليات</h4><span class="count">CONSOLE LOGS</span></div>
      <div class="console-box" id="consoleLogs">{% for log in bot_logs %}{{ log }}
{% else %}[Nexus Hosting] لوحة السجلات جاهزة.
{% endfor %}</div>
      <div class="ai-box"><div class="ai-icon"><i class="fa-solid fa-wand-magic-sparkles"></i></div><div><h4>مساعد تشخيص الأخطاء</h4><p>{{ ai_diagnosis }}</p></div></div>
    </section>
    {% else %}
    <section class="panel welcome"><div class="welcome-logo"><i class="fa-solid fa-rocket"></i></div><h2>ابدأ بإضافة أول بوت</h2><p>ستظهر هنا لوحة التحكم بمجرد إضافة بوت جديد.</p></section>
    {% endif %}
  </main>
</div>
{% else %}
<section class="panel welcome">
  <div class="welcome-logo"><i class="fa-solid fa-cubes-stacked"></i></div>
  <h2>كل بوتاتك. في مكان واحد.</h2>
  <p>لوحة تحكم عربية لإدارة بوتات ديسكورد بكل سهولة واحترافية.</p>
  <a href="/login" class="btn btn-discord btn-lg"><i class="fa-brands fa-discord ms-2"></i>المتابعة باستخدام Discord</a>
</section>
{% endif %}

<footer>© 2026 <strong>Nexus Hosting</strong> — جميع الحقوق محفوظة</footer>
</div>

{% if user %}
<!-- Modal إضافة بوت -->
<div class="modal fade" id="addBotModal" tabindex="-1"><div class="modal-dialog modal-dialog-centered"><div class="modal-content text-white">
  <div class="modal-header"><h5 class="modal-title fw-bold">إضافة بوت جديد</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
  <form action="/add_bot" method="POST"><div class="modal-body">
    <div class="mb-3"><label class="form-label">اسم البوت</label><input type="text" name="name" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">توكن البوت</label><input type="password" name="token" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">بادئة الأوامر</label><input type="text" name="prefix" value="!" class="form-control"></div>
    <div class="mb-2"><label class="form-label">اللغة</label><select name="lang" class="form-select"><option value="Python">Python</option><option value="JavaScript (Node.js)">JavaScript (Node.js)</option><option value="Lua">Lua</option><option value="TypeScript">TypeScript</option></select></div>
  </div><div class="modal-footer"><button type="submit" class="btn btn-nexus">حفظ وإضافة</button></div></form>
</div></div></div>

<!-- Modal ملفات البوت (تفتح بـ Ctrl + Shift + B) -->
<div class="modal fade" id="filesModal" tabindex="-1"><div class="modal-dialog modal-dialog-centered modal-lg"><div class="modal-content text-white">
  <div class="modal-header"><h5 class="modal-title fw-bold"><i class="fa-solid fa-folder-open text-warning ms-2"></i>مساحة رفع وتعديل ملفات البوت</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
  <form action="/save_bot_file" method="POST"><div class="modal-body">
    <div class="mb-3">
      <label class="form-label">اسم الملف (مثال: main.py أو config.json)</label>
      <input type="text" name="filename" class="form-control" value="main.py" required>
    </div>
    <div class="mb-3">
      <label class="form-label">محتوى الكود البرمجي (Python / Script)</label>
      <textarea name="code_content" class="form-control" rows="12" style="font-family:monospace;direction:ltr;text-align:left;" placeholder="# اكتب أو ألصق كود البوت هنا...">{{ sample_code }}</textarea>
    </div>
  </div><div class="modal-footer"><button type="button" class="btn btn-quiet" data-bs-dismiss="modal">إغلاق</button><button type="submit" class="btn btn-nexus">حفظ الملف بالسيرفر</button></div></form>
</div></div></div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
// تفعيل اختصارات لوحة المفاتيح
document.addEventListener('keydown', function(e) {
    // Ctrl + Shift + B لفتح نافذة الملفات
    if (e.ctrlKey && e.shiftKey && (e.key === 'B' || e.key === 'b')) {
        e.preventDefault();
        var filesModalEl = document.getElementById('filesModal');
        if (filesModalEl) {
            var modal = new bootstrap.Modal(filesModalEl);
            modal.show();
        }
    }
});

const logs=document.getElementById('consoleLogs');if(logs)logs.scrollTop=logs.scrollHeight;
</script>
</body></html>
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

    # تحميل نموذج كود افتراضي للعرض
    sample_code_path = BOT_FILES_DIR / "main.py"
    sample_code = sample_code_path.read_text(encoding="utf-8") if sample_code_path.exists() else "# اكتب كود بوت الديسكورد هنا\nimport discord\n"

    return render_template_string(
        HTML_TEMPLATE, 
        user=user, 
        user_bots=user_bots, 
        active_bot=active_bot, 
        selected_bot_idx=selected_bot_idx,
        bot_logs=bot_logs,
        ai_diagnosis=ai_diagnosis,
        is_admin=is_admin,
        admin_viewing=admin_viewing,
        viewing_user_id=viewing_user_id,
        sample_code=sample_code
    )

@app.route('/save_bot_file', methods=['POST'])
def save_bot_file():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    filename = request.form.get('filename', 'main.py').strip()
    code_content = request.form.get('code_content', '')
    
    # حماية ضد المسارات الضارة
    filename = os.path.basename(filename)
    file_path = BOT_FILES_DIR / filename
    
    file_path.write_text(code_content, encoding="utf-8")
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    user = session.get('user')
    if not user or user['id'] not in ADMIN_DISCORD_IDS:
        return "غير مأذون لك بالدخول إلى لوحة الأدمن.", 403
    
    all_bots_data = load_data(BOTS_FILE)
    users_map = load_data(USERS_FILE)
    
    return f"""
    <html dir="rtl"><body style="background:#0b0e14;color:#fff;font-family:Tahoma;padding:30px">
    <h2>🛡️ لوحة الأدمن الحصرية (الأدمن: {user['username']})</h2>
    <a href="/" style="color:#f3bd45">العودة للرئيسية</a>
    <hr>
    <pre>{json.dumps(all_bots_data, ensure_ascii=False, indent=2)}</pre>
    </body></html>
    """

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
    add_bot_log(user['id'], new_bot_idx, f"تم إضافة البوت بنجاح بلغة ({bot_lang}).")
    return redirect(url_for('index', bot=new_bot_idx))

@app.route('/bot_action/<int:bot_idx>/<action>')
def bot_action(bot_idx, action):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
        
    is_admin = user['id'] in ADMIN_DISCORD_IDS
    target_user_id = request.args.get('view_user') if is_admin else user['id']

    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(target_user_id, [])

    if bot_idx < len(user_bots):
        bot = user_bots[bot_idx]
        if action == 'start':
            bot['status'] = 'شغال'
            add_bot_log(target_user_id, bot_idx, f"▶️ تم تشغيل بوت ({bot['name']}) بنجاح.")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(target_user_id, bot_idx, f"⏹️ تم إيقاف بوت ({bot['name']}).")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(target_user_id, bot_idx, f"🔄 جاري إعادة تشغيل بوت ({bot['name']}).")
        
        save_data(BOTS_FILE, all_bots)

    redirect_url = url_for('index', bot=bot_idx)
    if target_user_id != user['id']:
        redirect_url += f"?view_user={target_user_id}"
    return redirect(redirect_url)

@app.route('/update_lang/<int:bot_idx>', methods=['POST'])
def update_lang(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
        
    is_admin = user['id'] in ADMIN_DISCORD_IDS
    target_user_id = request.args.get('view_user') if is_admin else user['id']

    new_lang = request.form.get('lang', 'Python')
    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(target_user_id, [])

    if bot_idx < len(user_bots):
        user_bots[bot_idx]['lang'] = new_lang
        save_data(BOTS_FILE, all_bots)
        add_bot_log(target_user_id, bot_idx, f"💻 تم تغيير لغة البوت إلى: {new_lang}")

    redirect_url = url_for('index', bot=bot_idx)
    if target_user_id != user['id']:
        redirect_url += f"?view_user={target_user_id}"
    return redirect(redirect_url)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
