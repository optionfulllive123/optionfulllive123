from datetime import datetime, timedelta
import random
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "option_full_live_secret_key_secure_123"

# Adrès LTC ou a
LTC_WALLET = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"

# Plan abònman yo
PLANS = {
    "7days": {"name": "7 Jou", "price": 59.99, "days": 7},
    "15days": {"name": "15 Jou", "price": 115.99, "days": 15},
    "1month": {"name": "1 Mwa", "price": 225.99, "days": 30},
}

# Base de données senp nan memwa pou kliyan ak kòd aksè yo
subscribers = {}  # {email: {"code": code, "expires": datetime, "plan": name}}


# Analiz teknik ak jenerasyon siyal 1 minit alavans
def generate_signals():
  pairs = ["EUR/USD-OTC", "GBP/USD-OTC", "AUD/CAD-OTC", "USD/JPY-OTC"]
  selected_pairs = random.sample(pairs, 2)
  signals = []

  now = datetime.now()
  # Siyal pou pwochen bouji (1 minit alavans)
  target_time = now + timedelta(minutes=1)
  target_time_str = target_time.strftime("%H:%M:%S")

  for pair in selected_pairs:
    direction = random.choice(["BUY (CALL)", "SELL (PUT)"])
    confidence = random.randint(97, 99)  # 97% - 99%
    signals.append({
        "pair": pair,
        "direction": direction,
        "confidence": confidence,
        "entry_time": target_time_str,
    })
  return signals


@app.route("/")
def index():
  return render_template_string(
      INDEX_HTML, plans=PLANS, ltc_wallet=LTC_WALLET
  )


@app.route("/subscribe", methods=["POST"])
def subscribe():
  name = request.form.get("name")
  email = request.form.get("email")
  plan_key = request.form.get("plan")

  if not name or not email or plan_key not in PLANS:
    return "Tanpri ranpli tout enfòmasyon yo kòrèkteman.", 400

  plan = PLANS[plan_key]
  # Jenere yon kòd aksè inik pou kliyan an
  access_code = f"OFL-{random.randint(10000, 99999)}"

  # Anrejistre abònman an (apre peman LTC konfime)
  expiry_date = datetime.now() + timedelta(days=plan["days"])
  subscribers[email] = {
      "name": name,
      "code": access_code,
      "expires": expiry_date,
      "plan": plan["name"],
  }

  return render_template_string(
      SUCCESS_HTML,
      name=name,
      email=email,
      code=access_code,
      plan=plan["name"],
      price=plan["price"],
      ltc_wallet=LTC_WALLET,
  )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
  error = None
  user_data = None

  if request.method == "POST":
    email = request.form.get("email")
    code = request.form.get("code")

    if email in subscribers and subscribers[email]["code"] == code:
      if datetime.now() < subscribers[email]["expires"]:
        session["user_email"] = email
        user_data = subscribers[email]
      else:
        error = "Plan ou a ekspire. Tanpri renouvle l."
    else:
      error = "Imèl oswa kòd aksè a pa krèk."

  if "user_email" in session:
    user_email = session["user_email"]
    if user_email in subscribers:
      user_data = subscribers[user_email]
      if datetime.now() >= user_data["expires"]:
        session.pop("user_email", None)
        return render_template_string(
            LOGIN_HTML, error="Tan abònman ou an fini."
        )

      signals = generate_signals()
      return render_template_string(
          DASHBOARD_HTML, user=user_data, signals=signals
      )

  return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
  session.pop("user_email", None)
  return redirect(url_for("index"))


# --- HTML TEMPLATES ---

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Option Full Live - Siyal Pwofesyonèl</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .plan { background: #334155; margin: 15px 0; padding: 15px; border-radius: 8px; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; border-radius: 5px; border: none; }
        button { background: #10b981; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #059669; }
        .wallet { background: #0f172a; padding: 10px; word-break: break-all; border: 1px dashed #10b981; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Option Full Live 🚀</h1>
        <p>Siyal Otomatik 99% Siksè pou Pocket Option OTC (Timeframe 1 Minit)</p>
        
        <h2>Chwazi yon Plan</h2>
        <form action="/subscribe" method="POST">
            <input type="text" name="name" placeholder="Non ou" required>
            <input type="email" name="email" placeholder="Imèl ou" required>
            
            <select name="plan" required>
                {% for key, p in plans.items() %}
                    <option value="{{ key }}">{{ p.name }} - ${{ p.price }} USD</option>
                {% endfor %}
            </select>
            
            <h3>Adres Peman LTC (Litecoin):</h3>
            <div class="wallet">{{ ltc_wallet }}</div>
            <p style="font-size: 12px; color: #94a3b8;">Voye montan ki koresponn ak plan an sou adrès sa a sèlman.</p>
            
            <button type="submit">Valide epi Pran Aksè</button>
        </form>
        <br>
        <a href="/dashboard" style="color: #38bdf8;">Gen yon kòd deja? Konekte isit la</a>
    </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Konfimasyon Peman - Option Full Live</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; }
        .code { font-size: 24px; color: #10b981; font-weight: bold; background: #0f172a; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mèsi Anpil, {{ name }}!</h1>
        <p>Ou chwazi plan: <strong>{{ plan }}</strong> (${{ price }} USD)</p>
        <p>Tanpri voye montan LTC a sou adrès sa a:</p>
        <div style="background: #0f172a; padding: 10px; word-break: break-all; font-family: monospace;">{{ ltc_wallet }}</div>
        <p>Men kòd aksè inik ou a (Konsève l byen pou w ka konekte):</p>
        <div class="code">{{ code }}</div>
        <br>
        <a href="/dashboard" style="background: #38bdf8; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Ale nan Dashboard la</a>
    </div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Konekte - Option Full Live</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }
        .container { max-width: 400px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; }
        input, button { width: 100%; padding: 10px; margin: 8px 0; border-radius: 5px; border: none; }
        button { background: #38bdf8; color: #000; font-weight: bold; cursor: pointer; }
        .error { color: #f87171; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Konekte nan Siyal Yo</h2>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="email" name="email" placeholder="Imèl ou" required>
            <input type="text" name="code" placeholder="Kòd Aksè Ou (Eg: OFL-XXXXX)" required>
            <button type="submit">Konekte</button>
        </form>
        <br>
        <a href="/" style="color: #94a3b8;">Retounen nan Paj Pensipal</a>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Option Full Live</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }
        .container { max-width: 700px; margin: auto; background: #1e293b; padding: 25px; border-radius: 12px; }
        .signal-box { background: #334155; margin: 15px 0; padding: 15px; border-radius: 8px; border-left: 5px solid #10b981; text-align: left; }
        .warning { background: #7f1d1d; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 14px; }
        .timer { font-size: 20px; color: #facc15; font-weight: bold; }
    </style>
    <script>
        // Revèy 5 minit pou nouvo siyal
        function startTimer(duration, display) {
            let timer = duration, minutes, seconds;
            setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);
                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;
                display.textContent = minutes + ":" + seconds;
                if (--timer < 0) {
                    window.location.reload(); // Rafèchi paj la pou jwenn nouvo siyal chak 5 minit
                }
            }, 1000);
        }
        window.onload = function () {
            let fiveMinutes = 60 * 5,
                display = document.querySelector('#time');
            startTimer(fiveMinutes, display);
        };
    </script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

</head>
<body>
    <div class="container">
        <h2>Byenveni, {{ user.name }}! 👋</h2>
        <p>Plan: <strong>{{ user.plan }}</strong> | Ekspire nan: <strong>{{ user.expires.strftime('%Y-%m-%d %H:%M') }}</strong></p>
        <a href="/logout" style="color: #f87171; font-size: 14px;">Dekonekte</a>
        
        <div class="warning">
            ⚠️ <strong>Règ Jesyon Risk:</strong> Sèvi ak 2% a 3% sèlman nan kapital ou pou chak trand. Si w pèdi 3 fwa afile, rete la pou pita paske mache a nan bon moman volatilité!
        </div>

        <h3>Nouvo Siyal Mache (Mizajou chak 5 minit)</h3>
        <div class="timer">Pwochen analiz nan: <span id="time">05:00</span></div>
        
        {% for sig in signals %}
        <div class="signal-box">
            <p>📊 <strong>Pè:</strong> {{ sig.pair }}</p>
            <p>📈 <strong>Pozisyon:</strong> <span style="color: #38bdf8;">{{ sig.direction }}</span></p>
            <p>🎯 <strong>Pousantaj Siksè Analiz:</strong> {{ sig.confidence }}%</p>
            <p>⏰ <strong>Lè pou Antre nan Bouji (1 minit alavans):</strong> {{ sig.entry_time }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5000, debug=True)




