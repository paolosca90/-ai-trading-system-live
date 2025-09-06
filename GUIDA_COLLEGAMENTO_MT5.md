# 🔌 Guida Completa: Collegamento MT5 per Nuovi Utenti
## AI Cash-Revolution - Integrazione MetaTrader 5

**Aggiornato:** 06 Settembre 2025  
**Per:** Utenti appena registrati al sistema

---

## 🎯 **PANORAMICA DEL PROCESSO**

Dopo esserti registrato e aver attivato il **trial gratuito di 7 giorni**, devi collegare il tuo account MetaTrader 5 per ricevere i segnali IA direttamente nella tua piattaforma di trading.

### **Flusso Completo:**
1. ✅ **Registrazione** → Trial 7 giorni attivato automaticamente
2. ✅ **Login** → Accesso alla dashboard personale  
3. 🔄 **Collegamento MT5** → Configurazione guidata
4. 📊 **Ricezione Segnali** → Automatica in MT5

---

## 📋 **REQUISITI PRELIMINARI**

### **Cosa ti serve:**
- ✅ Account AI Cash-Revolution attivo (registrazione completata)
- ✅ MetaTrader 5 installato sul tuo computer
- ✅ Account MT5 presso un broker supportato (Demo o Live)
- ✅ Connessione internet stabile

### **Broker Supportati:**
- 🏆 **IC Markets** (Raccomandato)
- 🏆 **Pepperstone** (Raccomandato) 
- 🏆 **XM** (Raccomandato)
- ⚡ Alpari
- ⚡ FxPro  
- 📞 Altri broker (contatta supporto)

---

## 🚀 **GUIDA STEP-BY-STEP**

### **STEP 1: Accedi alla Sezione MT5**
1. Effettua il **login** al tuo account AI Cash-Revolution
2. Clicca su **"MT5"** nella barra di navigazione
3. Verrai portato alla pagina di integrazione

### **STEP 2: Download e Installazione EA**

#### **Scaricare l'Expert Advisor (EA):**
1. Nella pagina MT5 Integration, clicca **"Download EA"**
2. Scarica il file `AI_Cash_Revolution_EA.ex5`
3. Salva il file in una cartella temporanea

#### **Installare l'EA in MT5:**
1. Apri MetaTrader 5
2. Vai su **"File" → "Apri Cartella Dati"**
3. Naviga in **"MQL5" → "Experts"**
4. Copia il file `AI_Cash_Revolution_EA.ex5` in questa cartella
5. Riavvia MetaTrader 5
6. L'EA apparirà nella sezione **"Expert Advisors"**

### **STEP 3: Configurazione dell'EA**

#### **Attivare l'EA su un Grafico:**
1. Apri un grafico qualsiasi (es. EUR/USD, M15)
2. Trascina l'EA `AI_Cash_Revolution_EA` sul grafico
3. Si aprirà la finestra delle impostazioni
4. **IMPORTANTE:** Abilita "Consenti trading automatico"
5. Clicca **"OK"**

#### **Generazione API Key:**
- L'EA genererà automaticamente una **API Key unica**
- Questa chiave apparirà nella scheda "Expert" di MT5
- **Copia questa chiave** - ti servirà per il collegamento

### **STEP 4: Collegamento Account**

#### **Nel sito AI Cash-Revolution:**
1. Torna alla pagina **MT5 Integration**
2. Clicca **"Connect Now"** nello Step 3
3. Compila il modulo con i tuoi dati MT5:

**Dati Richiesti:**
- 📝 **Numero Account MT5** (es. 12345678)
- 🌐 **Nome Server** (es. ICMarkets-Live02)  
- 🏢 **Nome Broker** (seleziona dalla lista)
- 💼 **Tipo Account** (Demo o Live)
- 🔑 **API Key** (generata dall'EA)

#### **Configurazioni Opzionali:**
- ✅ **Auto-Trade:** Esecuzione automatica segnali (consigliato per principianti)
- ✅ **Risk Management:** Gestione rischio integrata (ALTAMENTE consigliato)

4. Clicca **"Connect Account"**

### **STEP 5: Verifica Connessione**

#### **Controlli da Fare:**
1. ✅ **Stato Connessione:** Deve mostrare "Connected" in verde
2. ✅ **Dati Account:** Balance, Equity, Margin devono essere corretti
3. ✅ **Test Connection:** Clicca per verificare il collegamento
4. ✅ **EA Attivo:** In MT5 deve apparire una "faccia sorridente" sull'EA

---

## 📊 **COME FUNZIONANO I SEGNALI**

### **Ricezione Automatica:**
Una volta collegato, i segnali IA arriveranno automaticamente:

1. 🎯 **Segnale Generato** → Sistema IA analizza i mercati
2. 📡 **Invio Istantaneo** → Segnale inviato al tuo EA
3. ⚡ **Esecuzione** → EA apre la posizione in MT5 (se auto-trade è attivo)
4. 📱 **Notifica** → Ricevi conferma via app/email

### **Informazioni Incluse nel Segnale:**
- 💱 **Coppia Valutaria** (es. EUR/USD)
- 📈 **Direzione** (BUY/SELL)
- 💰 **Entry Price** (prezzo di entrata)
- 🛑 **Stop Loss** (gestione rischio)
- 🎯 **Take Profit** (obiettivo di profitto)
- 🧠 **Spiegazione IA** (perché questo segnale)
- 📊 **Affidabilità %** (confidence score)

---

## ⚙️ **CONFIGURAZIONI AVANZATE**

### **Gestione del Rischio:**
- 💵 **Lot Size:** Calcolato automaticamente in base al tuo balance
- 📊 **Max Risk per Trade:** Default 2% del capitale
- 🔢 **Max Trades Simultanei:** Default 3 posizioni
- ⏰ **Trading Hours:** Personalizzabili per fuso orario

### **Notifiche:**
- 📧 **Email:** Conferma apertura/chiusura posizioni
- 📱 **Push Notifications:** Segnali in tempo reale
- 💬 **Telegram Bot:** Canale privato segnali (Premium)

---

## 🔧 **RISOLUZIONE PROBLEMI COMUNI**

### **Problema: EA Non Connesso**
**Soluzioni:**
- ✅ Verifica connessione internet MT5
- ✅ Controlla che l'EA sia attivo sul grafico
- ✅ Verifica API Key sia corretta
- ✅ Riavvia MT5 e riconnetti EA

### **Problema: Segnali Non Arrivano**
**Soluzioni:**
- ✅ Verifica stato subscription (trial/attivo)
- ✅ Controlla impostazioni auto-trade
- ✅ Verifica orari di trading del broker
- ✅ Testa connessione dalla dashboard

### **Problema: Trades Non Eseguiti**
**Soluzioni:**
- ✅ Verifica balance minimo (>$100)
- ✅ Controlla leverage e margine disponibile
- ✅ Verifica che "Consenti trading automatico" sia attivo
- ✅ Controlla spread e condizioni di mercato

---

## 🎓 **BEST PRACTICES PER PRINCIPIANTI**

### **Raccomandazioni Iniziali:**
1. 🎯 **Inizia con Demo** - Testa tutto prima di usare soldi reali
2. 💰 **Capitale Minimo** - Almeno $500 per account live
3. ⚡ **Auto-Trade ON** - Lascia che l'IA gestisca tutto inizialmente
4. 📊 **Risk Management ON** - Sempre attivato
5. 📱 **Monitor Daily** - Controlla performance giornalmente

### **Errori da Evitare:**
- ❌ Non disattivare mai il Risk Management
- ❌ Non modificare manualmente i trade aperti dall'EA
- ❌ Non utilizzare leverage superiore a 1:100 inizialmente
- ❌ Non aprire posizioni manuali mentre l'EA è attivo

---

## 🆘 **SUPPORTO TECNICO**

### **Canali di Assistenza:**
- 💬 **Live Chat:** Disponibile 24/7 nella dashboard
- 📧 **Email:** support@ai-cash-revolution.com
- 📞 **Telefono:** +1-555-MATRIX (emergenze)
- 🎥 **Video Tutorial:** Disponibili in dashboard

### **Orari Supporto Prioritario:**
- ⏰ **Trial Users:** 9:00-18:00 CET
- ⚡ **Pro Users:** 24/7 con risposta garantita in 1 ora
- 🏆 **Enterprise:** Supporto dedicato + phone support

---

## 📈 **PROSSIMI PASSI**

### **Dopo il Collegamento:**
1. 📊 **Monitor Performance** - Controlla i risultati nei primi giorni
2. 💰 **Consider Upgrade** - Valuta upgrade a Pro dopo il trial
3. 📚 **Studia le Spiegazioni IA** - Impara dai segnali ricevuti
4. 🎯 **Ottimizza Settings** - Adatta le impostazioni alle tue preferenze

### **Upgrade Premium (Dopo Trial):**
- ⚡ **Segnali Prioritari** - Ricevi segnali con 2-3 secondi di anticipo
- 🎯 **Accuracy Più Alta** - Accesso ai segnali con >97% affidabilità  
- 📞 **Supporto VIP** - Assistenza prioritaria e call mensili
- 📊 **Analytics Avanzate** - Reportistica dettagliata performance

---

**🎉 Complimenti! Ora sei pronto a ricevere segnali IA direttamente in MT5!**

*Per domande specifiche o problemi tecnici, non esitare a contattare il nostro supporto disponibile 24/7.*

---

*Ultimo aggiornamento: 06 Settembre 2025*  
*AI Cash-Revolution - Trading Matrix System*