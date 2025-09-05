# Trading SaaS Backend - Sistema Centralizzato

## 🎯 DESCRIZIONE DEL SISTEMA

Sistema SaaS professionale per trading signals con:
- **Sistema centralizzato**: Analisi e ML sul server, esecuzione locale su MT5
- **Dati reali MT5**: Nessun costo API esterne, dati tick-level
- **AI Gemini**: Spiegazioni intelligenti per ogni segnale  
- **Machine Learning**: Sistema auto-apprendimento da risultati
- **Architettura scalabile**: Railway deployment ready

---

## 📁 STRUTTURA FILE

### File Core Sistema:
- **main.py**: API FastAPI completa con tutti gli endpoints
- **models.py**: Database models (User, Signal, Subscription, MT5Connection)
- **schemas.py**: Validazione Pydantic per API
- **jwt_auth.py**: Autenticazione JWT completa
- **signal_engine.py**: Motore professionale generazione segnali

### File Configurazione:
- **database.py**: Setup PostgreSQL per Railway  
- **auth.py**: Utilities hash password (bcrypt)
- **requirements.txt**: Dipendenze complete
- **Procfile**: Config deployment Railway
- **.gitignore**: File da ignorare in git

---

## 🚀 DEPLOYMENT RAILWAY

### 1. Environment Variables Richieste:

**SECRET_KEY** (obbligatorio): 
- Chiave per JWT tokens
- Genera con: `python -c "import secrets; print(secrets.token_hex(32))"`

**GEMINI_API_KEY** (opzionale):
- Per spiegazioni AI dei segnali
- Ottieni su: https://makersuite.google.com/app/apikey

**DATABASE_URL** (automatico):
- Railway lo fornisce automaticamente

### 2. Steps Deploy:

1. Carica tutti i file su GitHub
2. Collega repository a Railway
3. Aggiungi environment variables
4. Deploy automatico
5. Test su: `https://your-app.railway.app/docs`

---

## 🎯 ENDPOINTS API DISPONIBILI

### Autenticazione:
- `POST /register` - Registrazione con trial gratuito 7 giorni
- `POST /token` - Login con JWT tokens  
- `GET /me` - Profilo utente + statistiche complete

### Segnali Trading:
- `GET /signals/top` - Top 3 segnali pubblici (reliability ≥70%)
- `GET /signals` - Segnali utente con filtri avanzati
- `POST /signals` - Crea segnale (admin only)

### MetaTrader 5:
- `POST /mt5/connect` - Setup connessione MT5
- `GET /mt5/status` - Status connessione

### Sistema:
- `GET /health` - Health check
- `GET /docs` - Documentazione completa

---

## 💎 FUNZIONALITÀ PROFESSIONALI

### Sistema Segnali:
- **Analisi Tecnica**: RSI, MACD, Bollinger Bands, ATR, SMA/EMA
- **Price Action**: Pattern candele, trend analysis, supporti/resistenze
- **Scoring Affidabilità**: 0-100% basato su analisi multi-indicatore
- **Stop Loss/Take Profit**: Calcolati automaticamente con ATR
- **Spiegazioni AI**: Motivi del segnale con Gemini

### Gestione Utenti:
- **Trial Gratuito**: 7 giorni automatici alla registrazione
- **Statistiche Avanzate**: Win rate, P&L, reliability media
- **Sistema Subscription**: Gestione abbonamenti completa
- **Sicurezza JWT**: Tokens con refresh automatico

### Architettura:
- **Dati MT5 Reali**: Tick data, volumi, spread reali
- **Multi-timeframe**: Analisi M1 fino a Daily
- **Database Completo**: Tracking completo segnali e performance
- **Logging**: Sistema completo per debugging/monitoring

---

## 🔧 SVILUPPO LOCALE

```bash
# Installa dipendenze
pip install -r requirements.txt

# Setup environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://..."
export GEMINI_API_KEY="your-gemini-key"

# Avvia server
uvicorn main:app --reload

# Test API
open http://localhost:8000/docs
```

---

## 📊 PROSSIME FASI

### FASE 2 - Machine Learning (in sviluppo):
- Neural network per miglioramento segnali
- Auto-learning dai risultati trade
- Continuous training pipeline

### FASE 3 - MT5 Bridge Client:
- Executable Windows per utenti
- Auto-installazione MT5
- WebSocket real-time per segnali

### FASE 4 - Frontend Dashboard:
- React dashboard completa
- Visualizzazione segnali real-time
- Gestione abbonamenti e pagamenti

---

## 🎬 DEMO & TEST

1. **Registra utente**: POST `/register` - trial 7 giorni automatico
2. **Fai login**: POST `/token` - ottieni JWT
3. **Visualizza profilo**: GET `/me` - statistiche complete  
4. **Segnali top**: GET `/signals/top` - migliori segnali pubblici
5. **Setup MT5**: POST `/mt5/connect` - connessione trading

**Sistema pronto per produzione! 🚀**