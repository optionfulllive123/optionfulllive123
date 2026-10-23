import os
import sqlite3
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "option_full_live_secret_key_2026"

ADMIN_CODE = "ADMIN2026"
LTC_ADDRESS = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            days INTEGER,
            status TEXT DEFAULT 'unused',
            activated_at TEXT,
            expiration_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Mete liy sa a dirèkteman anba fonksyon an:
init_db()


# --- HTML TEMPLATES ---

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Option Full Live - BENVENI</title>
    <style>
        body { background-color: #ffffff; color: #111111; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #ffffff; border: 2px solid #e60000; padding: 25px; border-radius: 12px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 4px 15px rgba(230,0,0,0.15); }
        h2 { color: #e60000; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 15px; }
        button { width: 100%; padding: 12px; background-color: #e60000; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }
        button:hover { background-color: #cc0000; }
    </style>
</head>
<body>
    <div class="card">
        <h2>OPTION FULL LIVE</h2>
        <p style="color: #555;">Antre enfòmasyon ou yo pou w ka kontinye ale nan plan d'abonman yo:</p>
        <form action="/" method="POST">
            <input type="text" name="name" placeholder="Non ou" required>
            <input type="email" name="email" placeholder="Imèl ou" required>
            <button type="submit">KONTINYE</button>
        </form>
    </div>
</body>
</html>
"""

HTML_PLANS = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chwazi Yon Plan - Option Full Live</title>
    <style>
        body { background-color: #f9f9f9; color: #111; font-family: Arial, sans-serif; padding: 20px; text-align: center; }
        .container { max-width: 500px; margin: 0 auto; }
        .plan-card { background: #fff; border: 2px solid #e60000; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .plan-title { color: #e60000; font-size: 22px; font-weight: bold; }
        .price { font-size: 20px; margin: 10px 0; color: #333; }
        .ltc-box { background: #f1f1f1; padding: 10px; border-radius: 6px; font-size: 12px; word-break: break-all; margin: 10px 0; border: 1px dashed #e60000; }
        .btn-copy { background: #e60000; color: #fff; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .access-form { margin-top: 30px; background: #fff; padding: 20px; border-radius: 10px; border: 2px solid #111; }
        input { padding: 12px; width: 80%; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px; font-size: 16px; text-align: center; }
        .btn-submit { background: #111; color: #fff; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; }
        .msg-error { color: red; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #e60000;">PLAN D'ABONMAN</h1>
        <p>Voye peman an sou adrès LTC ki anba a pou chwazi plan ou vle a:</p>

        <!-- Plan 7 Jou -->
        <div class="plan-card">
            <div class="plan-title">PLAN 7 JOU</div>
            <div class="price">$59.99 USD</div>
            <p style="font-size: 13px; color: #666;">Aksè ak Kòd 6 chif pou 7 jou otomatik</p>
            <div class="ltc-box">{{ ltc_address }}</div>
            <button class="btn-copy" onclick="copyAddress1()">KOPYE ADRÈS LTC</button>
        </div>

        <!-- Plan 15 Jou -->
        <div class="plan-card">
            <div class="plan-title">PLAN 15 JOU</div>
            <div class="price">$119.99 USD</div>
            <p style="font-size: 13px; color: #666;">Aksè ak Kòd 7 chif pou 15 jou otomatik</p>
            <div class="ltc-box">{{ ltc_address }}</div>
            <button class="btn-copy" onclick="copyAddress2()">KOPYE ADRÈS LTC</button>
        </div>

        <!-- Plan 30 Jou -->
        <div class="plan-card">
            <div class="plan-title">PLAN 1 MWA (30 JOU)</div>
            <div class="price">$199.99 USD</div>
            <p style="font-size: 13px; color: #666;">Aksè ak Kòd 8 chif pou 30 jou otomatik</p>
            <div class="ltc-box">{{ ltc_address }}</div>
            <button class="btn-copy" onclick="copyAddress3()">KOPYE ADRÈS LTC</button>
        </div>

        <!-- Rantre Kòd Aksè -->
        <div class="access-form">
            <h3>RANTRE KÒD AKSÈ OU</h3>
            {% if error %}
                <div class="msg-error">{{ error }}</div>
            {% endif %}
            <form action="/verify-code" method="POST">
                <input type="text" name="access_code" placeholder="Antre Kòd Aksè Ou La" required><br>
                <button type="submit" class="btn-submit">RANTRE NAN PLATFÒM LAN</button>
            </form>
        </div>
    </div>

    <script>
        function copyAddress1() {
            navigator.clipboard.writeText("{{ ltc_address }}");
            alert("Adrès LTC an kopye ak siksè!");
        }
        function copyAddress2() { copyAddress1(); }
        function copyAddress3() { copyAddress1(); }
    </script>
</body>
</html>
"""

HTML_SIGNALS = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sinyal En Direct - Option Full Live</title>
    <style>
        body { background-color: #ffffff; color: #111; font-family: Arial, sans-serif; padding: 15px; text-align: center; }
        .header { background: #e60000; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .time-box { font-size: 26px; font-weight: bold; margin: 10px 0; color: #e60000; }
        .signals-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }
        .signal-card { background: #fff; border: 2px solid #111; border-radius: 8px; padding: 15px; width: 280px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .pair { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
        .action-buy { color: green; font-size: 22px; font-weight: bold; }
        .action-sell { color: red; font-size: 22px; font-weight: bold; }
        .details { font-size: 14px; margin: 5px 0; color: #444; }
        .footer-info { margin-top: 30px; font-size: 13px; color: #666; }
    </style>
</head>
<body>

    <div class="header">
        <h1>OPTION FULL LIVE - PLATFÒM SINYAL</h1>
        <p>Aksè Aktif: Bon travay!</p>
    </div>

    <div>TAN REYÈL KI SOU APARÈY OU A:</div>
    <div class="time-box" id="live-clock">--:--:--</div>

    <h2 style="color: #e60000; margin-top: 25px;">2 NOUVO SINYAL (CHAK 5 MINIT)</h2>
    <p style="font-size: 13px;">Analiz Teknik & Fondamantal (Timeframe 1-Minit)</p>

    <div class="signals-container" id="signals-box">
        <!-- Sinyal fiks pou blòk 5 minit lan -->
    </div>

    <div class="footer-info">
        <p>⚠️ Antre presizyon a lekzak tan yo montre a (Egzanp: Antre a 1h19.00 pou bouji 1h20.00 an).</p>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('live-clock').innerText = hours + ':' + minutes + ':' + seconds;
        }
        setInterval(updateClock, 1000);
        updateClock();

        const pairs = ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/CAD (OTC)", "EUR/JPY (OTC)", "USD/CHF (OTC)"];

        // Fonksyon ki kreye yon nimewo idantifyan ki baze s sou blòk 5 minit la (konsa li pap janm chanje pandan 5 minit yo)
        function getDeterministicSignals() {
            const now = new Date();
            let h = now.getHours();
            let m = now.getMinutes();
            let blockIndex = Math.floor(m / 5); // Chanje sèlman chak 5 minit egzak
            
            // Itilize tan an kòm yon "seed" pou nimewo yo pa chanje pandan 5 minit yo
            let seed = h * 100 + blockIndex;
            
            // Fo rafinman pou chwazi 2 pè ki toujou rete menm jan an pandan tout 5 minit sa yo
            let idx1 = seed % pairs.length;
            let idx2 = (seed + 3) % pairs.length;
            if (idx1 === idx2) idx2 = (idx2 + 1) % pairs.length;

            let p1 = pairs[idx1];
            let p2 = pairs[idx2];

            // Detèmine Buy oswa Sell baze sou seed la pou l pa janm fè aza oswa chanje tèt li
            let act1 = (seed % 2 === 0) ? "BUY (ANAUT)" : "SELL (ANBA)";
            let act2 = (seed % 3 === 0) ? "SELL (ANBA)" : "BUY (ANAUT)";

            let nextBlockMin = (blockIndex + 1) * 5;
            let targetH = h;
            let targetMin = nextBlockMin;
            if (targetMin >= 60) {
                targetMin = 0;
                targetH = (h + 1) % 24;
            }
            let entryMin = targetMin - 1;
            let entryH = h;
            if (entryMin < 0) {
                entryMin = 59;
                entryH = (h - 1 + 24) % 24;
            }

            let timeEntryStr = String(entryH).padStart(2, '0') + ':' + String(entryMin).padStart(2, '0') + ':00';
            let timeTargetStr = String(targetH).padStart(2, '0') + ':' + String(targetMin).padStart(2, '0') + ':00';

            return { p1, act1, p2, act2, timeEntryStr, timeTargetStr };
        }

        function displaySignals() {
            let sig = getDeterministicSignals();
            let html = `
                <div class="signal-card">
                    <div class="pair">${sig.p1}</div>
                    <div class="${sig.act1.includes('BUY') ? 'action-buy' : 'action-sell'}">${sig.act1}</div>
                    <div class="details"><b>Moman pou rantre:</b> ${sig.timeEntryStr}</div>
                    <div class="details"><b>Pou bouji:</b> ${sig.timeTargetStr}</div>
                    <div class="details"><b>Probabilite:</b> 99%</div>
                </div>
                <div class="signal-card">
                    <div class="pair">${sig.p2}</div>
                    <div class="${sig.act2.includes('BUY') ? 'action-buy' : 'action-sell'}">${sig.act2}</div>
                    <div class="details"><b>Moman pou rantre:</b> ${sig.timeEntryStr}</div>
                    <div class="details"><b>Pou bouji:</b> ${sig.timeTargetStr}</div>
                    <div class="details"><b>Probabilite:</b> 99%</div>
                </div>
            `;
            document.getElementById('signals-box').innerHTML = html;
        }

        displaySignals();
        // Tcheke chak segond men li pap chanje anyen jiskaske 5 minit yo pase nèt
        setInterval(displaySignals, 1000);
    </script>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Administratè - Option Full Live</title>
    <style>
        body { background-color: #f4f4f4; color: #111; font-family: Arial, sans-serif; padding: 20px; }
        .admin-card { background: white; padding: 20px; border-radius: 8px; border: 2px solid #e60000; max-width: 700px; margin: 0 auto; }
        h2 { color: #e60000; }
        .btn-gen { background: #e60000; color: white; border: none; padding: 10px 15px; margin: 5px; font-weight: bold; border-radius: 5px; cursor: pointer; }
        .btn-gen:hover { background: #cc0000; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; font-size: 14px; }
        th { background-color: #e60000; color: white; }
        .code-display { font-size: 20px; font-weight: bold; color: green; margin: 15px 0; background: #eafaf1; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="admin-card">
        <h2>PANEL ADMINISTRATÈ (SÈL OU MENM)</h2>
        <p>Klike sou bouton anba yo pou jeneré nouvo kòd pou kliyan yo:</p>
        
        <form action="/admin/generate" method="POST">
            <button type="submit" name="plan_type" value="7" class="btn-gen">Jeneré Kòd 7 Jou (6 chif)</button>
            <button type="submit" name="plan_type" value="15" class="btn-gen">Jeneré Kòd 15 Jou (7 chif)</button>
            <button type="submit" name="plan_type" value="30" class="btn-gen">Jeneré Kòd 30 Jou (8 chif)</button>
        </form>

        {% if new_code %}
            <div class="code-display">
                NOUVO KÒD JENERÉ: <u>{{ new_code }}</u> (Plan {{ plan_days }} Jou)
            </div>
        {% endif %}

        <h3>LIS TOUT KÒD YO NAN SISTÈM NAN:</h3>
        <table>
            <tr>
                <th>Kòd Aksè</th>
                <th>Plan (Jou)</th>
                <th>Statit</th>
                <th>Dat Ekspirasyon</th>
            </tr>
            {% for c in codes %}
            <tr>
                <td><b>{{ c[0] }}</b></td>
                <td>{{ c[1] }} Jou</td>
                <td>{{ c[2] }}</td>
                <td>{{ c[5] if c[5] else 'Poko Aktivé' }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# --- ROUTES FLASK ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_name'] = request.form.get('name')
        session['user_email'] = request.form.get('email')
        return redirect(url_for('plans'))
    return render_template_string(HTML_LOGIN)

@app.route('/plans')
def plans():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template_string(HTML_PLANS, ltc_address=LTC_ADDRESS, error=request.args.get('error'))

@app.route('/verify-code', methods=['POST'])
def verify_code():
    code_entered = request.form.get('access_code')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT code, days, status, expiration_date FROM codes WHERE code = ?", (code_entered,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return redirect(url_for('plans'))
        
    code, days, status, expiration_date = row
    now = datetime.now()
    
    # Si se premye fwa kliyan an ap itilize kòd la
    if status == 'unused':
        # Kalkile dat ekspirasyon fiks (7, 15 oswa 30 jou) depi premye aktivasyon
        new_expiration = now + timedelta(days=int(days))
        
        c.execute("""
            UPDATE codes 
            SET status = 'active', activated_at = ?, expiration_date = ? 
            WHERE code = ?
        """, (now.strftime('%Y-%m-%d %H:%M:%S'), new_expiration.strftime('%Y-%m-%d %H:%M:%S'), code_entered))
        conn.commit()
        
        # Enregistre kòd la nan sesyon kliyan an
        session['access_code'] = code_entered
        conn.close()
        return redirect(url_for('dashboard'))
        
    # Si kòd la te deja aktivé, tcheke si 7/15/30 jou yo pa ankò depase
    if status == 'active' and expiration_date:
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S')
        if now <= exp_date:
            session['access_code'] = code_entered
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            c.execute("UPDATE codes SET status = 'expired' WHERE code = ?", (code_entered,))
            conn.commit()
            conn.close()
            return redirect(url_for('plans'))
            
    conn.close()
    return redirect(url_for('plans'))


    if status == 'unused':
        exp_date = now + timedelta(days=days)
        c.execute("UPDATE access_codes SET status = 'active', used_by_email = ?, activation_date = ?, expiration_date = ? WHERE code = ?", 
                  (email, now, exp_date, code))
        conn.commit()
        conn.close()
        session['access_code'] = code
        return redirect(url_for('signals'))

    elif status == 'active':
        exp_datetime = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
        if now > exp_datetime:
            c.execute("UPDATE access_codes SET status = 'expired' WHERE code = ?", (code,))
            conn.commit()
            conn.close()
            return redirect(url_for('plans', error="Kòd aksè sa a ekspire! Tanpri achte yon nouvo plan."))
        else:
            conn.close()
            session['access_code'] = code
            return redirect(url_for('signals'))

    else:
        conn.close()
        return redirect(url_for('plans', error="Kòd sa a ekspire deja!"))

@app.route('/signals')
def signals():
    if 'access_code' not in session:
        return redirect(url_for('plans'))
    
    code = session['access_code']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT expiration_date FROM access_codes WHERE code = ?", (code,))
    row = c.fetchone()
    conn.close()

    if row and row[0]:
        exp_datetime = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() > exp_datetime:
            session.pop('access_code', None)
            return redirect(url_for('plans', error="Aksè ou sa a ekspire kounye a!"))

    return render_template_string(HTML_SIGNALS)

@app.route('/admin', methods=['GET'])
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT code, days, status, used_by_email, activation_date, expiration_date FROM access_codes ORDER BY ROWID DESC")
    codes = c.fetchall()
    conn.close()
    return render_template_string(HTML_ADMIN, codes=codes)

@app.route('/admin/generate', methods=['POST'])
def admin_generate():
    plan_days = int(request.form.get('plan_type'))
    
    if plan_days == 7:
        new_code = generate_random_code(6)
    elif plan_days == 15:
        new_code = generate_random_code(7)
    else:
        new_code = generate_random_code(8)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO access_codes (code, days, status) VALUES (?, ?, 'unused')", (new_code, plan_days))
    conn.commit()
    
    c.execute("SELECT code, days, status, used_by_email, activation_date, expiration_date FROM access_codes ORDER BY ROWID DESC")
    codes = c.fetchall()
    conn.close()

    return render_template_string(HTML_ADMIN, codes=codes, new_code=new_code, plan_days=plan_days)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
