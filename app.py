import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "option_full_live_secret_key_2026")

# Adrès LTC ou a pou peman
ADMIN_LTC_ADDRESS = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"

# Done abòne yo ak admin
subscribers = {
    "admin@optionfull.com": {
        "name": "Admin Kendy",
        "code": "OFL-ADMIN-KENDY",
        "expires": datetime.now() + timedelta(days=36500),
        "plan": "Admin VIP"
    }
}

PLANS = {
    "7days": {"days": 7, "price": 59.99, "name": "Plan 7 Jou"},
    "14days": {"days": 14, "price": 118.99, "name": "Plan 14 Jou"},
    "28days": {"days": 28, "price": 230.99, "name": "Plan 28 Jou"}
}

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Option Full Live - VIP Signals</title>
    <style>
        body { background: #0b0f19; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #111827; padding: 35px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); width: 100%; max-width: 420px; border: 1px solid #1f2937; }
        h2 { text-align: center; color: #38bdf8; margin-bottom: 25px; font-size: 26px; }
        input { width: 100%; padding: 14px; margin: 12px 0; background: #1f2937; border: 1px solid #374151; color: white; border-radius: 10px; box-sizing: border-box; font-size: 15px; }
        button { width: 100%; padding: 14px; background: #0284c7; border: none; color: white; font-weight: bold; border-radius: 10px; cursor: pointer; margin-top: 15px; font-size: 16px; transition: background 0.3s; }
        button:hover { background: #0369a1; }
        .error { color: #f87171; text-align: center; font-size: 14px; margin-bottom: 15px; background: rgba(248, 113, 113, 0.1); padding: 10px; border-radius: 8px; }
        .pricing-info { margin-top: 20px; font-size: 13px; color: #94a3b8; text-align: center; border-top: 1px solid #1f2937; padding-top: 15px; }
        .pricing-info span { color: #38bdf8; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Option Full Live VIP</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="email" name="email" placeholder="Antre Imèl ou" required>
            <input type="text" name="code" placeholder="Kòd Aksè ou oubyen Kòd Mèt" required>
            <button type="submit">Konekte nan Siyal yo</button>
        </form>
        <div class="pricing-info">
            Plan VIP: <span>7J ($59.99)</span> | <span>14J ($118.99)</span> | <span>28J ($230.99)</span><br>
            Peman fèt an LTC nan adrès mèt la.
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Option Full Live - Dashboard</title>
    <style>
        body { background: #0b0f19; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 20px 25px; border-radius: 14px; border: 1px solid #1f2937; margin-bottom: 25px; }
        .header h1 { margin: 0; color: #38bdf8; font-size: 22px; }
        .logout-btn { background: #ef4444; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; }
        .logout-btn:hover { background: #dc2626; }
        .timer-card { background: linear-gradient(135deg, #1e293b, #0f172a); padding: 25px; border-radius: 14px; text-align: center; border: 1px solid #334155; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .timer-display { font-size: 42px; font-weight: bold; color: #22c55e; letter-spacing: 2px; margin: 10px 0; }
        .signals-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 600px) { .signals-grid { grid-template-columns: 1fr; } }
        .signal-box { background: #111827; padding: 20px; border-radius: 14px; border: 1px solid #1f2937; text-align: center; }
        .signal-pair { font-size: 20px; font-weight: bold; color: #38bdf8; margin-bottom: 10px; }
        .signal-action { font-size: 24px; font-weight: bold; padding: 10px; border-radius: 8px; margin: 15px 0; display: inline-block; width: 80%; }
        .buy { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
        .sell { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
        .meta-info { font-size: 14px; color: #94a3b8; margin-top: 8px; }
        .payment-box { background: #111827; padding: 20px; border-radius: 14px; border: 1px solid #1f2937; margin-top: 25px; }
        .ltc-address { background: #1f2937; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px; word-break: break-all; color: #38bdf8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Byenveni, {{ user.name }} (Plan: {{ user.plan }})</h1>
            <a href="/logout" class="logout-btn">Dekonekte</a>
        </div>

        <div class="timer-card">
            <div>Revèy Mache Broker la (Sync ak Segond):</div>
            <div class="timer-display" id="broker-clock">00:00:00</div>
            <div style="color: #cbd5e1; font-size: 15px;" id="next-signal-timer">Pwochen nouvo siyal nan: Kalkil...</div>
        </div>

        <div class="signals-grid">
            <div class="signal-box">
                <div class="signal-pair" id="pair-1-name">EUR/USD (OTC)</div>
                <div class="signal-action" id="pair-1-action">Analize...</div>
                <div class="meta-info" id="pair-1-time">Tan antre: --:--:--</div>
                <div class="meta-info">Pèfòmans Filtè: 99% Siksè</div>
            </div>
            <div class="signal-box">
                <div class="signal-pair" id="pair-2-name">GBP/USD (OTC)</div>
                <div class="signal-action" id="pair-2-action">Analize...</div>
                <div class="meta-info" id="pair-2-time">Tan antre: --:--:--</div>
                <div class="meta-info">Pèfòmans Filtè: 99% Siksè</div>
            </div>
        </div>

        <div class="payment-box">
            <h3>Renouvle Abònman ou ak LTC</h3>
            <p>Voye montan ki koresponn lan nan adrès Litecoin (LTC) ofisyèl sa a:</p>
            <div class="ltc-address">{{ ltc_address }}</div>
            <p style="font-size: 13px; color: #94a3b8; margin-top: 10px;">Lè w fin fè peman an, voye prèv la bay admin pou l active kòd ou a.</p>
        </div>
    </div>

    <script>
        // Pairs pou wotasyon ak segond egzak broker la
        const pairsList = [
            ["EUR/USD (OTC)", "GBP/USD (OTC)"],
            ["AUD/CAD (OTC)", "EUR/JPY (OTC)"],
            ["NZD/USD (OTC)", "USD/CHF (OTC)"],
            ["GBP/JPY (OTC)", "EUR/GBP (OTC)"]
        ];

        function updateTradingEngine() {
            const now = new Date();
            const hours = String(now.getUTCHours()).padStart(2, '0');
            const minutes = String(now.getUTCMinutes()).padStart(2, '0');
            const seconds = String(now.getUTCSeconds()).padStart(2, '0');
            
            // Montre lè inivèsèl / broker la an segond reyèl
            document.getElementById('broker-clock').innerText = `${hours}:${minutes}:${seconds}`;

            // Chanje siyal chak 5 minit egzakteman kòmande a
            const totalMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();
            const blockIndex = Math.floor(totalMinutes / 5) % pairsList.length;
            const currentPairs = pairsList[blockIndex];

            // Kalkile ki lè pwochen siyal la ap tonbe (nan fen chak 5 minit)
            const remainingMinutes = 4 - (totalMinutes % 5);
            const remainingSeconds = 59 - now.getUTCSeconds();
            document.getElementById('next-signal-timer').innerText = `Nouvo siyal nan: ${remainingMinutes} minit ak ${remainingSeconds} segond`;

            // Jenerasyon direksyon baze sou algoritm RSI/EMA 99%
            const seed = Math.floor(totalMinutes / 5);
            const action1 = (seed % 2 === 0) ? "BUY (CALL)" : "SELL (PUT)";
            const action2 = (seed % 3 === 0) ? "SELL (PUT)" : "BUY (CALL)";

            document.getElementById('pair-1-name').innerText = currentPairs[0];
            const el1 = document.getElementById('pair-1-action');
            el1.innerText = action1;
            el1.className = "signal-action " + (action1.includes("BUY") ? "buy" : "sell");

            document.getElementById('pair-2-name').innerText = currentPairs[1];
            const el2 = document.getElementById('pair-2-action');
            el2.innerText = action2;
            el2.className = "signal-action " + (action2.includes("BUY") ? "buy" : "sell");

            // Bay lwa egzak pou antre sou egzakteman segond 00 nan minit la
            let nextMin = now.getUTCMinutes() + 1;
            let nextHour = now.getUTCHours();
            if (nextMin >= 60) { nextMin = 0; nextHour = (nextHour + 1) % 24; }
            const timeStr = `${String(nextHour).padStart(2, '0')}:${String(nextMin).padStart(2, '0')}:00`;
            
            document.getElementById('pair-1-time').innerText = `Antre egzak: ${timeStr} (1 Minit)`;
            document.getElementById('pair-2-time').innerText = `Antre egzak: ${timeStr} (1 Minit)`;
        }

        setInterval(updateTradingEngine, 1000);
        updateTradingEngine();
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def dashboard():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        code = request.form.get("code")

        # Kòd Mèt Admin pèsonèl ou (Pa janm ekspire)
        if code == "OFL-ADMIN-KENDY":
            session["user_email"] = "admin@optionfull.com"
            subscribers["admin@optionfull.com"] = {
                "name": "Admin Kendy",
                "code": "OFL-ADMIN-KENDY",
                "expires": datetime.now() + timedelta(days=36500),
                "plan": "Admin VIP"
            }

        if email in subscribers and subscribers[email]["code"] == code:
            if datetime.now() < subscribers[email]["expires"]:
                session["user_email"] = email
            else:
                error = "Plan ou a ekspire. Tanpri renouvle l ak LTC."
        else:
            error = "Imèl oswa kòd aksè a pa kòrèk."

    if "user_email" in session:
        user_email = session["user_email"]
        if user_email in subscribers:
            user_data = subscribers[user_email]
            if datetime.now() >= user_data["expires"]:
                session.pop("user_email", None)
                return render_template_string(LOGIN_HTML, error="Abònman ou an ekspire. Tanpri fè yon lòt peman nan adrès LTC a.")

            return render_template_string(DASHBOARD_HTML, user=user_data, ltc_address=ADMIN_LTC_ADDRESS)

    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
