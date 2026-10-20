import os
import sqlite3
import datetime
import random
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "option_full_live_secret_key_2026"

ADMIN_CODE = "ADMIN2026"  # Kòd sekrè pa w pou w gen aksè nan Dashboard la
LTC_ADDRESS = "ltc1qnn4la7cyv5xp7vqqsr4q8kqyjmc8gmekxu3s4z"

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS access_codes (
            code TEXT PRIMARY KEY,
            days INTEGER,
            start_date TIMESTAMP,
            expire_date TIMESTAMP,
            status TEXT DEFAULT 'unused'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    session['user_name'] = request.form.get('name')
    session['user_email'] = request.form.get('email')
    return redirect(url_for('plans'))

@app.route('/plans')
def plans():
    error = request.args.get('error')
    return render_template('plans.html', ltc_address=LTC_ADDRESS, error=error)

# PAJ KACHE POU OU KREYE KÒD POU KLIYAN YO
@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        admin_input = request.form.get('admin_code')
        if admin_input == ADMIN_CODE:
            session['is_admin'] = True

    if not session.get('is_admin'):
        return '''
            <div style="text-align:center; padding-top:50px; font-family:sans-serif; background:#121212; color:white; height:100vh;">
                <h2>Aksè Reservé pou Admin Sèlman 🔒</h2>
                <form method="POST">
                    <input type="password" name="admin_code" placeholder="Antre Kòd Admin W la" style="padding:10px; font-size:16px;" required>
                    <button type="submit" style="padding:10px 20px; background:#28a745; color:white; border:none; font-size:16px;">Antre</button>
                </form>
            </div>
        '''

    msg = None
    if request.method == 'POST' and 'new_code' in request.form:
        new_code = request.form.get('new_code').strip().upper()
        days = int(request.form.get('days'))
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO access_codes (code, days, status) VALUES (?, ?, 'unused')", (new_code, days))
            conn.commit()
            msg = f"✅ Kòd '{new_code}' pou {days} jou kreye ak siksè!"
        except Exception as e:
            msg = "❌ Kòd sa a te deja egziste! Chwazi yon lòt non kòd."
        conn.close()

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT code, days, status, expire_date FROM access_codes")
    codes_list = c.fetchall()
    conn.close()

    return render_template('admin.html', msg=msg, codes_list=codes_list)

@app.route('/verify-code', methods=['POST'])
def verify_code():
    code = request.form.get('code', '').strip().upper()
    now = datetime.datetime.now()

    if code == ADMIN_CODE:
        session['access_code'] = code
        session['is_admin'] = True
        return redirect(url_for('signals'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT days, start_date, expire_date, status FROM access_codes WHERE code=?", (code,))
    row = c.fetchone()

    if not row:
        conn.close()
        return redirect(url_for('plans', error="Kòd sa a pa egziste! Antre yon bon kòd."))

    days, start_date, expire_date, status = row

    if status == 'unused':
        exp_date = now + datetime.timedelta(days=days)
        c.execute("UPDATE access_codes SET start_date=?, expire_date=?, status='active' WHERE code=?",
                  (now.strftime("%Y-%m-%d %H:%M:%S"), exp_date.strftime("%Y-%m-%d %H:%M:%S"), code))
        conn.commit()
        conn.close()
        session['access_code'] = code
        return redirect(url_for('signals'))

    elif status == 'active':
        exp_dt = datetime.datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")
        if now > exp_dt:
            c.execute("UPDATE access_codes SET status='expired' WHERE code=?", (code,))
            conn.commit()
            conn.close()
            return render_template('expired.html', message=f"{days} jou abònman w lan fini nèt! Ranouvle plan w pou w gen aksè ankò.")
        else:
            conn.close()
            session['access_code'] = code
            return redirect(url_for('signals'))

    elif status == 'expired':
        conn.close()
        return render_template('expired.html', message="Kòd sa a fin ekspire! Li pa ka itilize ankò.")

    conn.close()
    return redirect(url_for('plans', error="Erè nan verifikasyon kòd la."))

@app.route('/signals')
def signals():
    code = session.get('access_code')
    if not code:
        return redirect(url_for('plans'))
    
    now = datetime.datetime.now()
    pairs = ["EUR/USD (OTC) 99%", "GBP/USD (OTC) 99%", "USD/JPY (OTC) 98%", "AUD/USD (OTC) 99%"]
    
    selected_pair = random.choice(pairs)
    direction = random.choice(["CALL 🟢 (BUY)", "PUT 🔴 (SELL)"])
    
    next_minute = (now + datetime.timedelta(minutes=1)).strftime("%H:%M:00")
    entry_time = (now + datetime.timedelta(minutes=2)).strftime("%H:%M:00")
    
    return render_template('signals.html', 
                           pair=selected_pair, 
                           direction=direction, 
                           signal_time=next_minute, 
                           entry_time=entry_time,
                           current_time=now.strftime("%H:%M:%S"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
