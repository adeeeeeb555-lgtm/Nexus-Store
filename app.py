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
app.secret_key = os.environ.get("SECRET_KEY", "nexus_super_secret_key_123")

# ==================== إعدادات تطبيق ديسكورد OAuth2 ====================
CLIENT_ID = "1557517949001007104"
CLIENT_SECRET = "2ZlOW2-lFDEUi8l-axCiJApzlCopidgM"
REDIRECT_URI = "https://nexus-store-6ktz.onrender.com/callback"

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
    if len(logs[key]) > 50:
        logs[key].pop(0)
    save_data(LOGS_FILE, logs)

# ==================== محاكي الذكاء الاصطناعي لتحليل المشاكل ====================
def ai_diagnose_issue(log_text, bot_name):
    log_lower = (log_text or "").lower()
    if "loginfailure" in log_lower or "token" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** التوكن الخاص بـ ({bot_name}) غير صحيح أو منتهي الصلاحية. يرجى التأكد من التوكن وإعادة إدخاله من جديد."
    elif "privilegedintentsrequired" in log_lower or "intent" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** البوت ({bot_name}) يفتقد لصلاحيات الـ Intents. يجب الدخول إلى Discord Developer Portal وتفعيل خيارات (Presence, Server Members, Message Content Intents)."
    elif "ratelimit" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** تم حظر البوت مؤقتًا بسبب كثرة الطلبات (Rate Limited). انتظر قليلاً ريثما يفك الحظر."
    elif "modulenotfound" in log_lower or "importerror" in log_lower:
        return f"⚠️ **تحليل الذكاء الاصطناعي (AI):** توجد مكتبة برمجية ناقصة مطلوبة لتشغيل كود البوت. تأكد من إضافتها في ملف متطلبات التشغيل."
    else:
        return f"✅ **تحليل الذكاء الاصطناعي (AI):** البوت ({bot_name}) يبدو مستقراً ولا توجد أخطاء حرجة ظاهرة في السجلات الحالية."

# ==================== تصميم الواجهة (HTML Template) ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Store • لوحة تحكم وإدارة البوتات الذكية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #07090e; color: #f3f6fb; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .nexus-card { background: #0d111a; border: 1px solid #1b2438; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .accent-text { color: #f5bc3a; }
        .btn-nexus { background-color: #f5bc3a; color: #07090e; font-weight: bold; border: none; }
        .btn-nexus:hover { background-color: #d99b26; color: #07090e; }
        .btn-discord { background-color: #5865F2; color: white; font-weight: bold; border: none; }
        .btn-discord:hover { background-color: #4752C4; color: white; }
        .avatar-img { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #f5bc3a; }
        .console-box { background: #080b12; color: #52d191; font-family: monospace; border-radius: 8px; padding: 15px; height: 220px; overflow-y: auto; border: 1px solid #1b2438; font-size: 13px; }
        .ai-box { background: #121722; border-left: 4px solid #f5bc3a; border-radius: 6px; padding: 12px; margin-top: 15px; font-size: 14px; }
        footer { border-top: 1px solid #1b2438; padding: 20px 0; margin-top: 40px; text-align: center; color: #6e7c99; }
    </style>
</head>
<body>
    <div class="container py-4">
        <!-- الهيدر والتسجيل -->
        <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h6 class="accent-text mb-0"><i class="fa-solid fa-server me-2"></i>NEXUS STORE HOSTING</h6>
                <h3 class="fw-bold mb-0">لوحة تحكم البوتات الذكية</h3>
            </div>
            <div>
                {% if user %}
                    <div class="d-flex align-items-center gap-3">
                        <img src="{{ user.avatar_url }}" class="avatar-img" alt="Avatar">
                        <div class="text-start">
                            <div class="fw-bold">{{ user.username }}</div>
                            <small class="text-muted">ID: {{ user.id }}</small>
                        </div>
                        <a href="/logout" class="btn btn-outline-danger btn-sm"><i class="fa-solid fa-right-from-bracket"></i> خروج</a>
                    </div>
                {% else %}
                    <a href="/login" class="btn btn-discord px-4 py-2">
                        <i class="fa-brands fa-discord me-2"></i> تسجيل الدخول عبر Discord
                    </a>
                {% endif %}
            </div>
        </div>

        {% if user %}
        <div class="row">
            <!-- قائمة البوتات وإضافة بوت -->
            <div class="col-md-4">
                <div class="nexus-card">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0"><i class="fa-solid fa-robot me-2"></i>بوتاتك</h5>
                        <button class="btn btn-nexus btn-sm" data-bs-toggle="modal" data-bs-target="#addBotModal">
                            <i class="fa-solid fa-plus me-1"></i> إضافة بوت
                        </button>
                    </div>
                    <div class="list-group">
                        {% for bot in user_bots %}
                        <a href="/?bot={{ loop.index0 }}" class="list-group-item list-group-item-action bg-dark text-white border-secondary mb-2 rounded {% if selected_bot_idx == loop.index0 %}active border-warning{% endif %}">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-1 fw-bold">{{ bot.name }}</h6>
                                <span class="badge {% if bot.status == 'شغال' %}bg-success{% else %}bg-danger{% endif %}">{{ bot.status }}</span>
                            </div>
                            <small class="text-muted">اللغة: {{ bot.lang }} | البريفكس: {{ bot.prefix }}</small>
                        </a>
                        {% else %}
                        <p class="text-muted text-center py-3">لم تقم بإضافة أي بوتات بعد.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- لوحة التحكم المخصصة للبوت المختار -->
            <div class="col-md-8">
                {% if active_bot %}
                <div class="nexus-card">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="fw-bold accent-text mb-0"><i class="fa-solid fa-sliders me-2"></i>إدارة البوت: {{ active_bot.name }}</h4>
                        <div>
                            <a href="/bot_action/{{ selected_bot_idx }}/start" class="btn btn-success btn-sm fw-bold"><i class="fa-solid fa-play me-1"></i> تشغيل</a>
                            <a href="/bot_action/{{ selected_bot_idx }}/stop" class="btn btn-danger btn-sm fw-bold"><i class="fa-solid fa-stop me-1"></i> إيقاف</a>
                            <a href="/bot_action/{{ selected_bot_idx }}/restart" class="btn btn-warning btn-sm fw-bold text-dark"><i class="fa-solid fa-rotate me-1"></i> إعادة تشغيل</a>
                        </div>
                    </div>

                    <!-- لوحة بيانات البوت وتغيير اللغة -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="p-3 bg-dark rounded border border-secondary">
                                <h6 class="fw-bold text-warning mb-2"><i class="fa-solid fa-circle-info me-2"></i>بيانات البوت</h6>
                                <p class="mb-1"><strong>الحالة:</strong> <span class="badge {% if active_bot.status == 'شغال' %}bg-success{% else %}bg-danger{% endif %}">{{ active_bot.status }}</span></p>
                                <p class="mb-1"><strong>بادئة الأوامر (Prefix):</strong> {{ active_bot.prefix }}</p>
                                <p class="mb-0"><strong>اللغة الحالية:</strong> {{ active_bot.lang }}</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="p-3 bg-dark rounded border border-secondary">
                                <h6 class="fw-bold text-warning mb-2"><i class="fa-solid fa-language me-2"></i>اختيار لغة البوت</h6>
                                <form action="/update_lang/{{ selected_bot_idx }}" method="POST" class="d-flex gap-2">
                                    <select name="lang" class="form-select bg-secondary text-white border-0 form-select-sm">
                                        <option value="العربية" {% if active_bot.lang == 'العربية' %}selected{% endif %}>العربية (Arabic)</option>
                                        <option value="الإنجليزية" {% if active_bot.lang == 'الإنجليزية' %}selected{% endif %}>الإنجليزية (English)</option>
                                        <option value="الفرنسية" {% if active_bot.lang == 'الفرنسية' %}selected{% endif %}>الفرنسية (French)</option>
                                    </select>
                                    <button type="submit" class="btn btn-nexus btn-sm">حفظ اللغة</button>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- لوحة اللوق (سجل العمليات والتشغيل) -->
                    <h5 class="fw-bold mb-2"><i class="fa-solid fa-terminal me-2"></i>سجل العمليات واللوق (Live Console)</h5>
                    <div class="console-box" id="consoleLogs">
                        {% for log in bot_logs %}
                            {{ log }}<br>
                        {% else %}
                            [Nexus System] لا توجد سجلات تشغيل لهذا البوت حتى الآن. اضغط على تشغيل لبدء البوت...
                        {% endfor %}
                    </div>

                    <!-- لوحة المساعد الذكي AI لتحليل المشاكل -->
                    <div class="ai-box">
                        <h6 class="fw-bold text-warning mb-1"><i class="fa-solid fa-wand-magic-sparkles me-2"></i>مساعد الذكاء الاصطناعي (AI Diagnostics)</h6>
                        <p class="mb-0">{{ ai_diagnosis }}</p>
                    </div>
                </div>
                {% else %}
                <div class="nexus-card text-center py-5">
                    <i class="fa-solid fa-hand-pointer display-4 text-muted mb-3"></i>
                    <h4 class="fw-bold">اختر بوت من القائمة الجانبية</h4>
                    <p class="text-muted">الرجاء اختيار أحد بوتاتك أو إضافة بوت جديد لعرض لوحة التحكم وإدارته بالكامل.</p>
                </div>
                {% endif %}
            </div>
        </div>
        {% else %}
        <div class="nexus-card text-center py-5">
            <i class="fa-brands fa-discord display-1 accent-text mb-3"></i>
            <h2 class="fw-bold">مرحباً بك في منصة Nexus Store</h2>
            <p class="text-muted col-md-8 mx-auto">قم بتسجيل الدخول بحساب ديسكورد للوصول إلى لوحات التحكم الخاصة ببوتاتك، إدارة التشغيل، اللوق، واللغات.</p>
            <a href="/login" class="btn btn-discord btn-lg px-5 mt-3">
                <i class="fa-brands fa-discord me-2"></i> الدخول باستخدام ديسكورد
            </a>
        </div>
        {% endif %}

        <footer>
            <p class="mb-1">جميع الحقوق محفوظة © <strong>Nexus Store</strong> 2026</p>
            <small class="text-muted">Powered by Nexus Store Advanced Management Engine</small>
        </footer>
    </div>

    <!-- Modal: إضافة بوت -->
    {% if user %}
    <div class="modal fade" id="addBotModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content bg-dark text-white border-secondary">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title">إضافة بوت جديد</h5>
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
                            <label class="form-label">لغة البوت الأساسية</label>
                            <select name="lang" class="form-select bg-secondary text-white border-0">
                                <option value="العربية">العربية</option>
                                <option value="الإنجليزية">الإنجليزية</option>
                                <option value="الفرنسية">الفرنسية</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                        <button type="submit" class="btn btn-nexus">حفظ البوت</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
    ai_diagnosis = "لم يتم تشخيص أي أخطاء بعد."
    selected_bot_idx = request.args.get('bot', type=int)

    if user:
        all_bots = load_data(BOTS_FILE)
        user_bots = all_bots.get(user['id'], [])
        
        if user_bots:
            if selected_bot_idx is None or selected_bot_idx >= len(user_bots):
                selected_bot_idx = 0
            active_bot = user_bots[selected_bot_idx]
            
            # جلب اللوق الخاص بالبوت
            all_logs = load_data(LOGS_FILE)
            bot_logs = all_logs.get(str(selected_bot_idx), [])
            
            # تشخيص المشكلة بواسطة الذكاء الاصطناعي بناءً على اللوق
            combined_logs = "\n".join(bot_logs)
            ai_diagnosis = ai_diagnose_issue(combined_logs, active_bot['name'])

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
    bot_lang = request.form.get('lang', 'العربية')

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
    add_bot_log(new_bot_idx, "تم إنشاء وإضافة البوت بنجاح إلى منصة Nexus Store.")
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
            add_bot_log(bot_idx, f"▶️ تم تشغيل البوت ({bot['name']}) بنجاح.")
        elif action == 'stop':
            bot['status'] = 'متوقف'
            add_bot_log(bot_idx, f"⏹️ تم إيقاف تشغيل البوت ({bot['name']}).")
        elif action == 'restart':
            bot['status'] = 'شغال'
            add_bot_log(bot_idx, f"🔄 جاري إعادة تشغيل البوت ({bot['name']})... البوت يعمل الآن.")
        
        save_data(BOTS_FILE, all_bots)

    return redirect(url_for('index', bot=bot_idx))

@app.route('/update_lang/<int:bot_idx>', methods=['POST'])
def update_lang(bot_idx):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    new_lang = request.form.get('lang', 'العربية')
    all_bots = load_data(BOTS_FILE)
    user_bots = all_bots.get(user['id'], [])

    if bot_idx < len(user_bots):
        user_bots[bot_idx]['lang'] = new_lang
        save_data(BOTS_FILE, all_bots)
        add_bot_log(bot_idx, f"🌐 تم تحديث لغة البوت إلى: {new_lang}")

    return redirect(url_for('index', bot=bot_idx))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
