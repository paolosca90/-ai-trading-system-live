# Trading Backend API - Railway Deploy

## File generati:

1. **requirements.txt** - Dipendenze Python
2. **Procfile** - Comando di avvio per Railway (rinomina in "Procfile" senza .txt)
3. **gitignore.txt** - File da ignorare in Git (rinomina in ".gitignore")
4. **database.py** - Configurazione database PostgreSQL
5. **models.py** - Modelli database (User, Signal)
6. **schemas.py** - Schema validazione API (Pydantic)
7. **main.py** - Applicazione FastAPI principale

## Istruzioni deploy su Railway:

### 1. Prepara i file:
- Rinomina "Procfile.txt" in "Procfile" (senza estensione)
- Rinomina "gitignore.txt" in ".gitignore"
- Gli altri file mantengono il nome originale

### 2. Genera una SECRET_KEY:
Vai su https://www.random.org/strings/ e genera una stringa casuale lunga
Oppure usa questo comando in Python:
```python
import secrets
print(secrets.token_hex(32))
```

### 3. Setup Railway:
1. Carica tutti i file su GitHub nel tuo repo
2. Su Railway dashboard:
   - Vai su Settings → Environment Variables
   - Aggiungi: `SECRET_KEY = [la tua stringa generata]`
   - DATABASE_URL viene fornita automaticamente da Railway

### 4. Test API:
Una volta deployato, vai su:
`https://tua-app.up.railway.app/docs`

## Funzionalità API:
- POST /register - Registrazione utenti
- POST /token - Login (restituisce JWT token)
- GET /me - Info utente autenticato
- POST /signals - Crea nuovo segnale
- GET /signals - Lista segnali utente

## Prossimi step:
1. Deploy backend
2. Test API con /docs
3. Sviluppo frontend React
4. Modulo generazione segnali
5. Eseguibile MT5 per clienti

Backend pronto per produzione con autenticazione sicura!