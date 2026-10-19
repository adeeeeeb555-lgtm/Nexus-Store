"""
===================================================================
 NEXUS STORE • Discord OAuth2 Login & Bot Hosting Manager
 Rights & Copyrights © Nexus Store - All Rights Reserved
===================================================================
"""
import os
import json
import requests
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nexus_super_secret_key_123")

# ==================== إعدادات تطبيق ديسكورد OAuth2 المدمجة ====================
CLIENT_ID = "1557517949001007104"
CLIENT_SECRET = "xdzPHlQUBJdnQoTTQjqVppxz1FNUgCIX"
REDIRECT_URI = "https://nexus-store-6ktz.onrender.com/callback"

DISCORD_API_BASE = "https://discord.com/api/v10"
OAUTH2_URL = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20email%20guilds"

# ==================== قواعد البيانات المحلية للحفظ ====================
BASE = Path(__file__).resolve().parent
USERS_FILE = BASE / "users_db.json"
BOTS_FILE = BASE / "user_bots.json"

def load_data(file_path):
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_data(file_path, data):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ==================== التصميم والتنسيق (HTML Template) ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Store • لوحة استضافة البوتات</title>
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
        footer { border-top: 1px solid #1b2438; padding: 20px 0; margin-top: 40px; text-align: center; color: #6e7c99; }
    </style>
</head>
<body>
    <div class="container py-4">
        <!-- الشريط العلوي والتسجيل -->
        <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h6 class="accent-text mb-0"><i class="fa-solid fa-server me-2"></i>NEXUS STORE HOSTING</h6>
                <h3 class="fw-bold mb-0">استضافة البوتات السحابية</h3>
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
        <!-- لوحة التحكم الخاصة بالمستخدم بعد تسجيل الدخول -->
        <div class="row">
            <div class="col-md-5">
                <div class="nexus-card">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0"><i class="fa-solid fa-robot me-2"></i>بوتاتك المضافة</h5>
                        <button class="btn btn-nexus btn-sm" data-bs-toggle="modal" data-bs-target="#addBotModal">
                            <i class="fa-solid fa-plus me-1"></i> إضافة بوت
                        </button>
                    </div>
                    <div class="list-group">
                        {% for bot in user_bots %}
                        <div class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center mb-2 rounded">
                            <div>
                                <h6 class="mb-1 fw-bold">{{ bot.name }}</h6>
                                <small class="text-muted">البريفكس: {{ bot.prefix }}</small>
                            </div>
                            <span class="badge bg-success">نشط</span>
                        </div>
                        {% else %}
                        <p class="text-muted text-center py-3">لم تقم بإضافة أي بوتات بعد.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <div class="col-md-7">
                <div class="nexus-card">
                    <h5 class="fw-bold mb-3"><i class="fa-solid fa-shield-halved me-2"></i>معلومات الحساب والتخزين</h5>
                    <p class="text-muted">تم ربط حسابك في ديسكورد بنجاح وحفظ بياناتك تلقائياً في قاعدة بيانات Nexus Store.</p>
                    <ul class="list-group list-group-flush bg-transparent">
                        <li class="list-group-item bg-transparent text-white border-secondary">
                            <strong>البريد الإلكتروني:</strong> {{ user.email or 'غير متوفر' }}
                        </li>
                        <li class="list-group-item bg-transparent text-white border-secondary">
                            <strong>حالة الاشتراك:</strong> <span class="badge bg-warning text-dark">خطة مجانية (Free Tier)</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        {% else %}
        <!-- صفحة الترحيب قبل تسجيل الدخول -->
        <div class="nexus-card text-center py-5">
            <i class="fa-brands fa-discord display-1 accent-text mb-3"></i>
            <h2 class="fw-bold">مرحباً بك في منصة Nexus Store</h2>
            <p class="text-muted col-md-8 mx-auto">قم بتسجيل الدخول باستخدام حسابك في Discord للوصول إلى لوحة استضافة وإدارة بوتاتك الخاصة مع الحفظ التلقائي لقاعدة البيانات.</p>
            <a href="/login" class="btn btn-discord btn-lg px-5 mt-3">
                <i class="fa-brands fa-discord me-2"></i> الدخول باستخدام ديسكورد
            </a>
        </div>
        {% endif %}

        <footer>
            <p class="mb-1">جميع الحقوق محفوظة © <strong>Nexus Store</strong> {{ current_year }}</p>
            <small class="text-muted">Powered by Nexus Store Hosting Engine</small>
        </footer>
    </div>

    <!-- Modal: إضافة بوت -->
    {% if user %}
    <div class="modal fade" id="addBotModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content bg-dark text-white border-secondary">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title">إضافة بوت جديد لحسابك</h5>
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

# ==================== المسارات والمنطق (Routes) ====================

@app.route('/')
def index():
    user = session.get('user')
    user_bots = []
    if user:
        all_bots = load_data(BOTS_FILE)
        user_bots = all_bots.get(user['id'], [])
    return render_template_string(HTML_TEMPLATE, user=user, user_bots=user_bots, current_year="2026")

@app.route('/login')
def login():
    return redirect(OAUTH2_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('index'))

    # 1. استبدال الـ Code بـ Access Token
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

    # 2. جلب بيانات المستخدم من Discord API
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

    # 3. حفظ بيانات المستخدم في الجلسة وفي ملف قاعدة البيانات المحلي
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

    all_bots = load_data(BOTS_FILE)
    if user['id'] not in all_bots:
        all_bots[user['id']] = []

    all_bots[user['id']].append({
        'name': bot_name,
        'token': bot_token,
        'prefix': bot_prefix
    })

    save_data(BOTS_FILE, all_bots)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
