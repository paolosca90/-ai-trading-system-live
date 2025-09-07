# 🖥️ VPS APPLICAZIONE - AI TRADING SYSTEM

## 📋 ARCHITETTURA SISTEMA

```
🌐 Railway (Cloud)           🖥️ VPS (Windows) 
├── Interface Web            ├── MetaTrader 5 Terminal
├── Login/Registrazione      ├── MT5 Bridge Server  
├── Database Utenti          ├── AI Signal Engine
└── Frontend HTML/CSS/JS     ├── Machine Learning Engine
                             ├── Database Segnali
                             └── Gemini AI Integration
```

## 🎯 RESPONSABILITÀ VPS

La VPS si occupa di **TUTTO il sistema di trading AI**:
- ✅ Connessione diretta MT5
- ✅ Analisi tecnica avanzata (RSI, MACD, Bollinger, ATR)  
- ✅ Generazione segnali con ML (reliability ≥70%)
- ✅ Spiegazioni AI tramite Gemini
- ✅ Database locale segnali per performance
- ✅ MT5 Bridge API per Railway

## 📁 FILE NECESSARI SULLA VPS

### 🔧 File Core Sistema
```
📂 VPS_Trading_System/
├── 📄 main_vps.py              # Server principale VPS
├── 📄 signal_engine.py         # Motore generazione segnali
├── 📄 ml_engine.py             # Machine Learning algoritmi
├── 📄 mt5_bridge_server.py     # Bridge MT5 per Railway
├── 📄 ai_signal_generator.py   # Generator segnali AI
├── 📄 database_vps.py          # Database VPS locale  
├── 📄 models_vps.py            # Modelli database VPS
├── 📄 schemas_vps.py           # Schemi dati VPS
└── 📄 requirements_vps.txt     # Dipendenze VPS
```

### 📄 File Configurazione
```
├── 📄 .env_vps                 # Variabili ambiente VPS
├── 📄 config_vps.py            # Configurazioni sistema
├── 📄 mt5_symbols.json         # Lista simboli broker
└── 📄 trading_parameters.json  # Parametri trading AI
```

### 🤖 File AI/ML
```
├── 📄 gemini_integration.py    # Integrazione Gemini AI
├── 📄 technical_analysis.py    # Analisi tecnica avanzata
├── 📄 pattern_recognition.py   # Riconoscimento pattern
├── 📄 risk_management.py       # Gestione rischio
└── 📄 backtesting_engine.py    # Backtesting segnali
```

## 🚀 GUIDA INSTALLAZIONE VPS

### 1️⃣ PREREQUISITI VPS
```bash
# VPS Windows Server 2019/2022
# RAM: minimo 8GB (consigliato 16GB)
# CPU: minimo 4 core
# Storage: minimo 100GB SSD
# Internet: connessione stabile
```

### 2️⃣ INSTALLAZIONE SOFTWARE BASE
```bash
# 1. Python 3.12
https://www.python.org/downloads/

# 2. MetaTrader 5 Terminal
https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# 3. Git per Windows
https://git-scm.com/download/win

# 4. Visual Studio Code (opzionale)
https://code.visualstudio.com/
```

### 3️⃣ SETUP PROGETTO VPS
```bash
# Clona repository
git clone https://github.com/paolosca90/-ai-trading-system-live.git
cd -ai-trading-system-live

# Installa dipendenze Python VPS
pip install -r requirements_vps.txt

# Le dipendenze includono:
# - MetaTrader5>=5.0.5260
# - TA-Lib>=0.6.7  
# - google-generativeai>=0.8.5
# - pandas>=2.0.0
# - numpy>=1.24.0
# - sqlalchemy>=2.0.0
# - fastapi>=0.104.0
# - uvicorn>=0.24.0
```

### 4️⃣ CONFIGURAZIONE MT5
```bash
# 1. Avvia MetaTrader 5
# 2. Accedi al tuo account broker
# 3. Abilita "Allow automated trading"
# 4. Abilita "Allow DLL imports" 
# 5. Verifica connessione server broker
```

### 5️⃣ CONFIGURAZIONE AMBIENTE
```bash
# Crea file .env_vps
MT5_BROKER_SERVER=TuoServer.exe
MT5_LOGIN=123456
MT5_PASSWORD=tuapassword
MT5_BRIDGE_PORT=8000
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_VPS_URL=sqlite:///vps_trading.db
LOG_LEVEL=INFO
BRIDGE_HOST=0.0.0.0
```

### 6️⃣ AVVIO SISTEMA VPS
```bash
# Terminal 1: Avvia MT5 Bridge Server  
python mt5_bridge_server.py

# Terminal 2: Avvia Signal Engine
python main_vps.py

# Terminal 3: Avvia ML Engine (opzionale)
python ml_engine.py
```

## 🔧 CONFIGURAZIONE AVANZATA

### 🎯 Simboli Trading
Modifica `mt5_symbols.json`:
```json
{
  "major_pairs": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"],
  "minor_pairs": ["EURGBP", "EURJPY", "GBPJPY"],
  "metals": ["XAUUSD", "XAGUSD"],
  "indices": ["US500", "US30", "NAS100"],
  "min_reliability": 70,
  "max_signals_per_hour": 5
}
```

### 🧠 Parametri AI
Modifica `trading_parameters.json`:
```json
{
  "rsi_period": 14,
  "macd_fast": 12,
  "macd_slow": 26,
  "bollinger_period": 20,
  "atr_period": 14,
  "min_score_buy": 35,
  "min_score_sell": -35,
  "gemini_enabled": true,
  "ml_confidence_threshold": 0.75
}
```

## 📊 MONITORAGGIO SISTEMA

### 🔍 Log Files
```bash
📂 logs/
├── 📄 mt5_bridge.log          # Log connessione MT5
├── 📄 signal_engine.log       # Log generazione segnali  
├── 📄 ml_engine.log           # Log Machine Learning
└── 📄 system.log              # Log sistema generale
```

### 📈 Performance Monitoring
```bash
# URL monitoraggio (VPS locale)
http://localhost:8000/health        # Status sistema
http://localhost:8000/api/stats     # Statistiche segnali
http://localhost:8000/api/mt5/info  # Info connessione MT5
```

## 🔐 SICUREZZA VPS

### 🛡️ Checklist Sicurezza
- ✅ Firewall Windows attivo
- ✅ Solo porte necessarie aperte (8000, 3389)
- ✅ Password amministratore forte
- ✅ Windows Update automatici
- ✅ Antivirus attivo
- ✅ Backup database giornalieri

### 🔑 API Key Security
```bash
# Non committare mai .env_vps!
echo ".env_vps" >> .gitignore
echo "*.log" >> .gitignore
echo "vps_trading.db" >> .gitignore
```

## 🔄 BACKUP E RIPRISTINO

### 💾 Backup Automatico
```bash
# Script backup giornaliero (Windows Task Scheduler)
python backup_system.py --daily
```

### 📋 Cosa fare in caso di crash
1. Controlla log files in `logs/`
2. Verifica connessione MT5 broker
3. Riavvia MT5 Bridge: `python mt5_bridge_server.py`
4. Riavvia Signal Engine: `python main_vps.py`
5. Controlla database: verificare `vps_trading.db`

## 🆘 TROUBLESHOOTING

### ❌ Errori Comuni
| Errore | Causa | Soluzione |
|--------|-------|-----------|
| MT5 disconnesso | Broker offline/credenziali | Ricontrolla login MT5 |
| Gemini API fail | API key invalida | Verifica GEMINI_API_KEY |
| Database lock | Processo duplicato | Termina processi multipli |
| Porte occupate | Software conflitto | Cambia porta in config |

### 📞 Supporto Tecnico
- 📧 Log completi in `logs/system.log`
- 🔍 Database status: `python check_db.py`
- 📊 MT5 connection test: `python test_mt5.py`

---

## 🎯 RISULTATO FINALE

Con questa configurazione avrai:
- ✅ **VPS**: Sistema AI completo con MT5 diretto
- ✅ **Railway**: Solo interfaccia web sicura  
- ✅ **Utenti**: Accesso ai segnali via web
- ✅ **Performance**: Sistema ottimizzato e scalabile
- ✅ **Sicurezza**: Separazione responsabilità

**Il sistema VPS genera i segnali, Railway li mostra agli utenti!** 🚀