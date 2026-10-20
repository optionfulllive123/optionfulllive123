import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "cle_sekre_option_full_live_123"

# ==========================================
# CONFIGURATION (Mete Enfòmasyon pa w yo la)
# ==========================================
LTC_WALLET_ADDRESS = "RANPLASE_AK_ADRES_LTC_SAFEPAL_OU"
TELEGRAM_USERNAME = "RANPLASE_AK_USERNAME_TELEGRAM_OU"

# Pristri Plan yo
PLANS = {
    "1_month": {"name": "Plan 1 Mwa (30 Jou)", "days": 30, "price_usd": 20},
    "3_months": {"name": "Plan 3 Mwa (90 Jou)", "days": 90, "price_usd": 50},
    " lifetime":{"name": "Plan Unilimité", "days": 3650, "price_usd": 150} # 10 ans
}

# ==========================================
# BAZ DE DONE (sqlite3)
# ==========================================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            selected_plan TEXT,
            copied_ltc INTEGER DEFAULT 0,
            is_paid INTEGER DEFAULT 0,
            expiration_date DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 1. ENREGISTREMENT (Non + Email)
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    
    if not name or not email:
        return redirect(url_for('index'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Enregistre ou met à jour le client
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('INSERT INTO users (name, email, is_paid) VALUES (?, ?, 0)', (name, email))
    else:
        cursor.execute('UPDATE users SET name = ? WHERE email = ?', (name, email))
        
    conn.commit()
    conn.close()
    
    session['user_email'] = email
    
    # Voye li sou paj plan yo dirèkteman
    return redirect(url_for('plans'))

# ==========================================
# 2. SELEKSYON PLAN YO
# ==========================================
@app.route('/plans')
def plans():
    if not session.get('user_email'):
        return redirect(url_for('index'))
    return render_template('plans.html', plans=PLANS)

@app.route('/select-plan', methods=['POST'])
def select_plan():
    email = session.get('user_email')
    plan_key = request.form.get('plan')
    
    if not email or plan_key not in PLANS:
        return redirect(url_for('plans'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET selected_plan = ? WHERE email = ?', (plan_key, email))
    conn.commit()
    conn.close()
    
    return redirect(url_for('payment'))

# ==========================================
# 3. PAJ PEMAN LTC & KOPIE ADRES
# ==========================================
@app.route('/payment')
def payment():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('index'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT selected_plan FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    plan_info = PLANS.get(user[0]) if user else None
    
    return render_template('payment.html', 
                           ltc_address=LTC_WALLET_ADDRESS, 
                           telegram=TELEGRAM_USERNAME,
                           plan=plan_info)

@app.route('/mark-copied', methods=['POST'])
def mark_copied():
    # Yo klike sou kopie adrès LTC a
    email = session.get('user_email')
    if email:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Jwenn jou plan an pou kalkile dat ekspirasyon
        cursor.execute('SELECT selected_plan FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        plan_key = row[0] if row else "1_month"
        days_to_add = PLANS.get(plan_key, {}).get('days', 30)
        
        # Preprasyon aksè an
        exp_date = datetime.now() + timedelta(days=days_to_add)
        exp_str = exp_date.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('UPDATE users SET copied_ltc = 1, is_paid = 1, expiration_date = ? WHERE email = ?', (exp_str, email))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

# ==========================================
# 4. PAJ SIYAL BOT LA (Aksè pwoteje ak Lè Reyèl)
# ==========================================
@app.route('/signals')
def signals():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('index'))
        
    # Pran lè local/reyèl aparèy la si li pase l nan paramèt query (oswa lè sèvè a)
    client_time_str = request.args.get('user_time')
    if client_time_str:
        try:
            current_time = datetime.strptime(client_time_str, '%Y-%m-%d %H:%M:%S')
        except:
            current_time = datetime.now()
    else:
        current_time = datetime.now()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT copied_ltc, is_paid, expiration_date FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    # 1. Si li poko kopie adrès la oswa poko valide: BLOKE!
    if not user or user[0] != 1 or user[1] != 1:
        return redirect(url_for('payment'))
        
    # 2. Kontwòl jou yo ak lè reyèl: Si dat la depase, KOUPE AKSÈ A!
    exp_date = datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S')
    if current_time > exp_date:
        return render_template('expired.html', message="Abònman ou an fini! Tanpri chwazi yon nouvo plan pou renouvle.")

    # Si tout bagay an règ, li jwenn siyal bot la!
    return render_template('signals.html', current_time=current_time)

# ==========================================
# 5. EXECUTION DÉMARRAGE
# ==========================================
if __name__ == '__main__':
    # Nou kenbe menm port 5000 lan san nou pa anyen nan rezo a
    app.run(host='0.0.0.0', port=5000, debug=True)
