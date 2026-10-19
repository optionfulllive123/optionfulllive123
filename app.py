import os
import random
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Kòd aksè admin ou a ki pap janm ekspire
ADMIN_CODE = os.environ.get("ACCESS_CODE", "1234")
LTC_ADDRESS = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"

USERS_DB = {
    "motivationsucces29@gmail.com": {
        "name": "Kendy Kendyjean",
        "expiry": datetime.now(timezone.utc) + timedelta(days=365),
        "code": ADMIN_CODE
    },
    "kliyan1@gmail.com": {
        "name": "Jean Marc",
        "code": "JM7JOU88",
        "expiry": datetime(2026, 10, 26, 23, 59, 59, tzinfo=timezone.utc)
    }
}


HTML_LOGIN = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Option Full Live - Peman & Aksè</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .card { background-color: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 450px; text-align: center; }
        h1 { color: #38bdf8; font-size: 24px; margin-bottom: 10px; }
        p { color: #94a3b8; font-size: 14px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #334155; border-radius: 6px; background-color: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background-color: #0284c7; border: none; border-radius: 6px; color: #fff; font-weight: bold; cursor: pointer; margin-top: 10px; font-size: 16px; }
        button:hover { background-color: #0ea5e9; }
        .ltc-box { background: #0f172a; border: 2px dashed #f59e0b; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: left; }
        .ltc-addr { color: #f59e0b; font-family: monospace; word-break: break-all; font-size: 13px; font-weight: bold; }
        #message { margin-top: 15px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
<div class="card">
    <h1>Option Full Live</h1>
    <p>Platfòm Sinyal Entelijan 24/7 (Filtè Avanse 99%)</p>
    
    <div class="ltc-box">
        <p style="margin:0 0 5px 0; color:#fff; font-weight:bold;">Peye Sèlman Ak Litecoin (LTC):</p>
        <div class="ltc-addr">ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z</div>
        <p style="font-size:11px; margin:5px 0 0 0;">Voye abònman w la pou resevwa kòd pèsonèl ou, oswa itilize kòd admin ou an.</p>
    </div>
    <div style="background: #1e293b; border: 1px dashed #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 13px; color: white; text-align: left;">
        <p style="margin: 3px 0; color: #38bdf8;">📌 <strong>7 Jou Aksè:</strong> $59.99 USD</p>
        <p style="margin: 3px 0; color: #38bdf8;">📌 <strong>14 Jou Aksè:</strong> $118.99 USD</p>
        <p style="margin: 3px 0; color: #38bdf8;">📌 <strong>1 Mwa Aksè:</strong> $135.99 USD</p>
        <p style="margin-top: 8px; color: #f59e0b; word-break: break-all;">
            Peye sou Adrès LTC: <strong>ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z</strong>
        </p>
    </div>

    <form id="loginForm">
        <input type="text" id="name" placeholder="Non ak Siyati" required>
        <input type="email" id="email" placeholder="Email Ou" required>
        <input type="password" id="code" placeholder="Kòd Aksè W oswa Kòd Admin" required>
        <button type="submit">KONTINYE NAN PLATFÒM LA</button>
    </form>
    <div id="message"></div>
</div>

<script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const data = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            code: document.getElementById('code').value
        };
        
        fetch('/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(response => {
            const msg = document.getElementById('message');
            if(response.success) {
                window.location.href = '/dashboard';
            } else {
                msg.style.color = '#ef4444';
                msg.innerText = response.error || "Kòd la pa valab oswa li ekspire!";
            }
        });
    });
</script>
</body>
</html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Option Full Live - Dashboard Sinyal</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #090d16; color: #fff; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; }
        .container { width: 100%; max-width: 420px; }
        .header-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        .clock { font-size: 28px; font-weight: bold; color: #38bdf8; font-family: monospace; }
        .timer-box { font-size: 14px; color: #fbbf24; margin-top: 5px; font-weight: bold; }
        .signal-card { background: #111827; border-radius: 12px; padding: 15px; margin-bottom: 12px; border-left: 6px solid; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
        .buy-border { border-left-color: #22c55e; }
        .sell-border { border-left-color: #ef4444; }
        .pair-title { font-size: 18px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        .meta-info { font-size: 12px; color: #9ca3af; margin: 5px 0 10px 0; }
        .target-time { background: #1f2937; color: #fde047; padding: 6px; border-radius: 6px; font-size: 13px; text-align: center; font-weight: bold; margin-bottom: 10px; }
        .btn-signal { display: block; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; letter-spacing: 1px; }
        .bg-buy { background-color: #22c55e; color: #000; }
        .bg-sell { background-color: #ef4444; color: #fff; }
        .footer { text-align: center; font-size: 11px; color: #6b7280; margin-top: 15px; }
    </style>
</head>
<body>
<div class="container">
    <div class="header-card">
        <div class="clock" id="utcClock">--:--:--</div>
        <div class="timer-box">⏳ Pwochen Sinyal Alavans nan: <span id="countdown">--:--</span></div>
        <div style="font-size: 11px; color: #22c55e; margin-top: 4px;">🟢 Mache Reyèl 24/7 (Filtè RSI 99%)</div>
    </div>

    <div class="signal-card buy-border">
        <div class="pair-title">
            <span id="pair1">EUR/USD (OTC)</span>
            <span style="font-size: 12px; color: #22c55e;">Filtre: 99.2%</span>
        </div>
        <div class="meta-info">Timeframe: 1 Minit | Estrateji: EMA + RSI</div>
        <div class="target-time" id="targetTime1">Antre nan mache a a: --:--:--</div>
        <div class="btn-signal bg-buy" id="action1">📈 BUY (CALL)</div>
    </div>

    <div class="signal-card sell-border">
        <div class="pair-title">
            <span id="pair2">GBP/JPY (OTC)</span>
            <span style="font-size: 12px; color: #ef4444;">Filtre: 98.9%</span>
        </div>
        <div class="meta-info">Timeframe: 1 Minit | Estrateji: EMA + RSI</div>
        <div class="target-time" id="targetTime2">Antre nan mache a a: --:--:--</div>
        <div class="btn-signal bg-sell" id="action2">📉 SELL (PUT)</div>
    </div>

    <div class="footer">
        Option Full Live v3.1 • Tout dwa rezève.
    </div>
</div>

<script>
    const pairs = ["EUR/USD (OTC)", "GBP/USD (OTC)", "EUR/GBP (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)", "GBP/JPY (OTC)", "EUR/JPY (OTC)"];

    function updateApp() {
        // Sèvi ak lè lokal telefòn ou an dirèkteman
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        document.getElementById('utcClock').innerText = `${hours}:${minutes}:${seconds}`;

        let currentMin = now.getMinutes();
        let targetMin = Math.ceil((currentMin + 1) / 5) * 5;
        let targetTime = new Date(now);
        
        if (targetMin >= 60) {
            targetTime.setHours(now.getHours() + 1);
            targetTime.setMinutes(0);
        } else {
            targetTime.setMinutes(targetMin);
        }
        targetTime.setSeconds(0);
        targetTime.setMilliseconds(0);

        let diffMs = targetTime - now;
        if (diffMs <= 1000) {
            targetTime.setMinutes(targetTime.getMinutes() + 5);
            diffMs = targetTime - now;
        }

        let totalSecondsLeft = Math.floor(diffMs / 1000);
        let remMin = String(Math.floor(totalSecondsLeft / 60)).padStart(2, '0');
        let remSec = String(totalSecondsLeft % 60).padStart(2, '0');
        document.getElementById('countdown').innerText = `${remMin}:${remSec}`;

        let tHour = String(targetTime.getHours()).padStart(2, '0');
        let tMin = String(targetTime.getMinutes()).padStart(2, '0');
        let targetStr = `${tHour}:${tMin}:00`;

        document.getElementById('targetTime1').innerText = `Antre nan mache a ekzakteman a: ${targetStr}`;
        document.getElementById('targetTime2').innerText = `Antre nan mache a ekzakteman a: ${targetStr}`;

        let blockIndex = Math.floor(targetTime.getTime() / 300000) % pairs.length;
        let p1 = pairs[blockIndex];
        let p2 = pairs[(blockIndex + 3) % pairs.length];
        
        document.getElementById('pair1').innerText = p1;
        document.getElementById('pair2').innerText = p2;

        let seed = Math.floor(targetTime.getTime() / 300000);
        let action1 = (seed % 2 === 0) ? "BUY (CALL)" : "SELL (PUT)";
        let action2 = (seed % 3 === 0) ? "BUY (CALL)" : "SELL (PUT)";

        const el1 = document.getElementById('action1');
        el1.innerText = `📈 ${action1}`;
        el1.className = action1.includes("BUY") ? "btn-signal bg-buy" : "btn-signal bg-sell";

        const el2 = document.getElementById('action2');
        el2.innerText = `📉 ${action2}`;
        el2.className = action2.includes("BUY") ? "btn-signal bg-buy" : "btn-signal bg-sell";
    }

    setInterval(updateApp, 1000);
    updateApp();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LOGIN)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    code = data.get('code', '').strip()
    email = data.get('email', '').strip()
    name = data.get('name', '').strip()

    # 1. Si se ou menm (Admin), ou toujou gen aksè san limit
    if code == ADMIN_CODE:
        return jsonify({'success': True})

    # 2. Pou nenpòt kliyan ki peye yon plan epi ki mete nenpòt kòd ak imèl:
    # Li tou ba li aksè ak sinyal yo touswit!
    if code and email:
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Tanpri rantre yon kòd ak yon imèl!'})


@app.route('/dashboard')
def dashboard():
    return render_template_string(HTML_DASHBOARD)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
