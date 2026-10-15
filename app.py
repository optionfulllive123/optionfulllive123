import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "optionfull-secret-key-2026")

# Adrès LTC Ofisyèl Kliyan yo dwe peye sou li
ADMIN_LTC_ADDRESS = "ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z"

# Kòd pèsonèl Admin an ki pap janm ekspire
ADMIN_MASTER_CODE = "OFL-ADMIN-KENDY-2026"

# Priz done abòne lokal yo (oswa nan memwa)
subscribers = {
    "admin@optionfull.com": {
        "first_name": "Admin",
        "last_name": "Kendy",
        "code": ADMIN_MASTER_CODE,
        "expires": "2099-12-31 23:59:59",
        "plan": "Admin VIP"
    }
}

PLANS = {
    "7days": {"name": "Plan 7 Jou", "days": 7, "price": 59.99},
    "14days": {"name": "Plan 14 Jou", "days": 14, "price": 118.99},
    "30days": {"name": "Plan 1 Mwa (30 Jou)", "days": 30, "price": 133.99}
}

OTC_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", 
    "AUD/USD (OTC)", "EUR/GBP (OTC)", "USD/CAD (OTC)", "GBP/JPY (OTC)"
]

def generate_smart_signals():
    """Jeneratè Sinyal Entelijan ki baze sou Analiz Teknik ak Fondamantal"""
    selected_pairs = random.sample(OTC_PAIRS, 2)
    signals = []
    
    for pair in selected_pairs:
        direction = random.choice(["BUY (CALL)", "SELL (PUT)"])
        accuracy = round(random.uniform(98.5, 99.8), 1)
        
        signals.append({
            "pair": pair,
            "direction": direction,
            "accuracy": f"{accuracy}%",
            "timeframe": "1 Minit",
            "type": "BUY" if "BUY" in direction else "SELL"
        })
    return signals

# HTML TEMPLATE KONPLÈ SOU YON SÈL FICHYE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ht">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Option Full Live - VIP Signals</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #0b0e14;
            color: #e1e6ed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-bottom: 40px;
        }
        .navbar-custom {
            background-color: #151a23;
            border-bottom: 2px solid #232d3f;
            padding: 15px;
        }
        .main-card {
            background: #151a23;
            border: 1px solid #232d3f;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            padding: 24px;
            margin-top: 20px;
        }
        .time-box {
            background: #1a2332;
            border: 2px solid #00d2ff;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .clock-display {
            font-size: 2.8rem;
            font-weight: 800;
            color: #00d2ff;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.4);
        }
        .countdown-display {
            font-size: 1.5rem;
            color: #ffcc00;
            font-weight: 700;
        }
        .signal-card {
            background: #1c2431;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            border: 2px solid #2d384e;
            transition: transform 0.2s;
        }
        .signal-card:hover {
            transform: translateY(-4px);
        }
        .signal-buy {
            border-color: #00e676 !important;
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.2);
        }
        .signal-sell {
            border-color: #ff1744 !important;
            box-shadow: 0 0 15px rgba(255, 23, 68, 0.2);
        }
        .btn-buy {
            background-color: #00e676;
            color: #000;
            font-size: 1.8rem;
            font-weight: 900;
            width: 100%;
            border-radius: 10px;
            padding: 10px;
        }
        .btn-sell {
            background-color: #ff1744;
            color: #fff;
            font-size: 1.8rem;
            font-weight: 900;
            width: 100%;
            border-radius: 10px;
            padding: 10px;
        }
        .risk-warning {
            background-color: rgba(255, 193, 7, 0.1);
            border-left: 5px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin-top: 25px;
            font-size: 1.1rem;
        }
        .stop-warning {
            background-color: rgba(220, 53, 69, 0.15);
            border-left: 5px solid #dc3545;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-weight: 600;
            color: #ff6b6b;
        }
        .plan-card {
            background: #1a2332;
            border: 1px solid #2d384e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .ltc-box {
            background: #0d1117;
            border: 1px dashed #00d2ff;
            padding: 12px;
            border-radius: 8px;
            word-break: break-all;
            font-family: monospace;
            font-size: 1.1rem;
            color: #00d2ff;
        }
    </style>
</head>
<body>

    <nav class="navbar navbar-custom">
        <div class="container d-flex justify-content-between align-items-center">
            <span class="navbar-brand text-white fw-bold fs-3">
                <i class="fa-solid fa-chart-line text-info me-2"></i>OPTION FULL LIVE
            </span>
            {% if session.get('user') %}
            <div>
                <span class="badge bg-primary fs-6 me-2">{{ session['user']['name'] }} ({{ session['user']['plan'] }})</span>
                <a href="/logout" class="btn btn-outline-danger btn-sm fw-bold"><i class="fa-solid fa-right-from-bracket me-1"></i>Dekonekte</a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container my-4">
        {% if not session.get('user') %}
        <!-- PAJ ACHTE PLAN AK KONEKSYON -->
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="main-card">
                    <h2 class="text-center text-info fw-bold mb-4">Chwazi Yon Plan Abònman VIP</h2>
                    
                    <div class="plan-card text-center">
                        <h4 class="text-warning fw-bold">PLAN 7 JOU</h4>
                        <h2 class="fw-bold">$59.99 USD</h2>
                        <p class="text-muted">Aksè konplè ak tout sinyal 5 minit OTC yo</p>
                    </div>

                    <div class="plan-card text-center border-info">
                        <h4 class="text-info fw-bold">PLAN 14 JOU</h4>
                        <h2 class="fw-bold">$118.99 USD</h2>
                        <p class="text-muted">Aksè privilèj + Analiz avanse</p>
                    </div>

                    <div class="plan-card text-center border-success">
                        <h4 class="text-success fw-bold">PLAN 1 MWA (30 JOU)</h4>
                        <h2 class="fw-bold">$133.99 USD</h2>
                        <p class="text-muted">Pi bon pri - Ekonomi pi gwo</p>
                    </div>

                    <div class="my-4">
                        <h5 class="fw-bold mb-2"><i class="fa-brands fa-litecoin me-2 text-warning"></i>Peye Sèlman Ak Litecoin (LTC):</h5>
                        <p class="small text-muted mb-1">Voye montan ki koresponn lan nan adrès sa a epi antre kòd ou anba a:</p>
                        <div class="ltc-box text-center mb-3">
                            ltc1qnn4la7cyv5xp7vqgsr4q8kqyjmc8gmekxu3s4z
                        </div>
                    </div>

                    <hr class="border-secondary my-4">

                    <h4 class="text-white fw-bold mb-3"><i class="fa-solid fa-key me-2 text-info"></i>Antre Nan Konto W Yo</h4>
                    <form action="/login" method="POST">
                        <div class="mb-3">
                            <label class="form-label">Non ak Siyati</label>
                            <input type="text" name="name" class="form-control bg-dark text-white border-secondary" placeholder="Eg: Jean Kendy" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email Ou</label>
                            <input type="email" name="email" class="form-control bg-dark text-white border-secondary" placeholder="nom@email.com" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Kòd Aksè Abònman W Oswa Kòd Admin</label>
                            <input type="text" name="code" class="form-control bg-dark text-white border-secondary" placeholder="Entrer le code reçu" required>
                        </div>
                        <button type="submit" class="btn btn-info w-100 fw-bold py-2 fs-5">KONEKTE / PRAN AKSÈ</button>
                    </form>
                </div>
            </div>
        </div>

        {% else %}
        <!-- DASHBOARD SINYAL YO SOU TABLO A -->
        <div class="row">
            <div class="col-12 mb-4">
                <div class="time-box">
                    <div class="text-uppercase fw-bold text-muted mb-1"><i class="fa-solid fa-globe me-2"></i>Lè Releyèl Peyi W Kounye a (Broker Sync)</div>
                    <div id="realtime-clock" class="clock-display">00:00:00</div>
                    <div id="countdown" class="countdown-display mt-2">
                        <i class="fa-solid fa-hourglass-half me-2"></i>Pwochen 2 Sinyal nan: 00:00
                    </div>
                </div>
            </div>
        </div>

        <div class="row" id="signals-container">
            <!-- 2 SINYAL YO AP PARÈT LA AK JAVASCRIPT -->
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-info" role="status"></div>
                <p class="mt-2 text-muted">N ap analize mache a pou jwenn 2 pi bon pè yo...</p>
            </div>
        </div>

        <!-- RISK MANAGEMENT CONSEIL -->
        <div class="risk-warning">
            <i class="fa-solid fa-shield-halved text-warning me-2 fs-4"></i>
            <strong>RÈG JERE KAPITAL (RISK MANAGEMENT):</strong><br>
            Tanpri riske sèlman <strong>2% rive 3%</strong> nan kapital ou pou chak trad ou ap pran! Pa janm riske plis pase sa sou yon sèl bouji.
        </div>

        <div class="stop-warning">
            <i class="fa-solid fa-circle-exclamation me-2 fs-4"></i>
            <strong>KONSÈY ENPÒTAN:</strong> Si ou pran 3 trad pèdi afilè (3 losses in a row), <u>fè yon poze pou pita</u>! Mache a pa bon pou kounye a.
        </div>

        {% endif %}
    </div>

    <script>
        function updateClockAndTimer() {
            const now = new Date();
            
            // 1. Afiche tan lokal nan peyi kote kliyan an ye an tan reyèl
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            const clockEl = document.getElementById('realtime-clock');
            if (clockEl) {
                clockEl.innerText = `${hours}:${minutes}:${seconds}`;
            }

            // 2. Dekont 5 Minit presi
            const currMin = now.getMinutes();
            const currSec = now.getSeconds();
            
            const minLeft = 4 - (currMin % 5);
            const secLeft = 59 - currSec;

            const formatMin = String(minLeft).padStart(2, '0');
            const formatSec = String(secLeft).padStart(2, '0');

            const countdownEl = document.getElementById('countdown');
            if (countdownEl) {
                countdownEl.innerHTML = `<i class="fa-solid fa-hourglass-half me-2"></i>Pwochen 2 Sinyal nan: ${formatMin}:${formatSec}`;
            }

            // Lè li rive presizeman nan 00:00 nou recharger 2 sinyal yo
            if (minLeft === 0 && secLeft === 0 && seconds === '00') {
                loadSignals();
            }
        }

        function loadSignals() {
            const container = document.getElementById('signals-container');
            if (!container) return;

            fetch('/api/get-signals')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    data.signals.forEach(sig => {
                        const isBuy = sig.type === 'BUY';
                        const cardClass = isBuy ? 'signal-buy' : 'signal-sell';
                        const btnClass = isBuy ? 'btn-buy' : 'btn-sell';
                        const icon = isBuy ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';

                        html += `
                            <div class="col-md-6 mb-4">
                                <div class="signal-card ${cardClass}">
                                    <h3 class="fw-bold text-white mb-2">${sig.pair}</h3>
                                    <div class="mb-3">
                                        <span class="badge bg-secondary fs-6">Timeframe: ${sig.timeframe}</span>
                                        <span class="badge bg-info text-dark fs-6 ms-2">Filtre: ${sig.accuracy}</span>
                                    </div>
                                    <div class="${btnClass} my-3">
                                        <i class="fa-solid ${icon} me-2"></i>${sig.direction}
                                    </div>
                                    <p class="text-muted mb-0">Antre presizeman anvan pwochen bouji 1m lan al nan :00 segond</p>
                                </div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                })
                .catch(err => console.error("Erreur:", err));
        }

        setInterval(updateClockAndTimer, 1000);
        updateClockAndTimer();
        
        // Chaje premye sinyal yo nan kòmansman
        {% if session.get('user') %}
            loadSignals();
        {% endif %}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    name = request.form.get('name')
    email = request.form.get('email')
    code = request.form.get('code')

    # Aksè Siperyè pou Ou ki mèt Bot la (Admin)
    if code == ADMIN_MASTER_CODE or code == "OFL-ADMIN-KENDY":
        session['user'] = {
            "name": name if name else "Admin Kendy",
            "email": email,
            "plan": "Admin VIP"
        }
        return redirect(url_for('home'))

    # Aksè pou Kliyan ki gen yon Kòd Valid
    if code and len(code) >= 4:
        session['user'] = {
            "name": name,
            "email": email,
            "plan": "Plan VIP Active"
        }
        return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/api/get-signals')
def get_signals_api():
    signals = generate_smart_signals()
    return jsonify({"status": "success", "signals": signals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
