//+------------------------------------------------------------------+
//|                                    AI_Cash_Revolution_EA.mq5     |
//|                        Copyright 2025, AI Cash-Revolution Ltd    |
//|                                   https://ai-cash-revolution.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, AI Cash-Revolution Ltd"
#property link      "https://ai-cash-revolution.com"
#property version   "2.0"
#property description "AI Cash-Revolution Expert Advisor - Ricevi segnali IA direttamente in MT5"

//--- Input parameters
input group "=== CONNESSIONE API ==="
input string API_URL = "https://your-api-domain.com";  // URL del tuo server API
input string API_KEY = "";  // Inserire la propria API Key dalla web-app
input int HeartbeatInterval = 30;  // Invia heartbeat ogni X secondi
input bool EnableAutoTrading = true;  // Attiva esecuzione automatica ordini
input int MinConfidencePercent = 70;  // Esegui solo segnali con confidenza >= %

input group "=== GESTIONE RISCHIO ==="
input double MaxRiskPercent = 2.0;  // Rischio massimo per trade (%)
input double MaxLotSize = 1.0;  // Lotto massimo per trade
input int MaxSimultaneousTrades = 3;  // Massimo trade simultanei
input bool EnableStopLoss = true;  // Attiva Stop Loss automatico
input bool EnableTakeProfit = true;  // Attiva Take Profit automatico

input group "=== IMPOSTAZIONI TRADING ==="
input int MagicNumber = 777888;  // Magic Number per identificare i trade
input int Slippage = 3;  // Slippage massimo (punti)
input bool EnableTradeLog = true;  // Log dettagliato delle operazioni
input bool SendNotifications = true;  // Invia notifiche push

input group "=== ORARI TRADING ==="
input bool EnableTradingHours = false;  // Limita orari di trading
input int StartHour = 8;   // Ora inizio trading
input int EndHour = 22;    // Ora fine trading

//--- Global variables
string UniqueID = "";
datetime LastHeartbeat = 0;
int TotalTrades = 0;
double TotalProfit = 0.0;
bool IsConnected = false;
string ConnectionStatus = "Disconnesso";
bool PendingOrderExists = false;

//--- Structures
struct Signal {
    string symbol;
    int type;           // 0=BUY, 1=SELL
    double entry_price;
    double stop_loss;
    double take_profit;
    double lot_size;
    int confidence;
    string explanation;
    datetime timestamp;
    bool executed;
};

Signal CurrentSignals[];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    // Genera ID unico per questo EA
    GenerateUniqueID();
    
    // Mostra informazioni iniziali
    Print("=== AI Cash-Revolution EA v2.0 Inizializzato ===");
    Print("UniqueID: ", UniqueID);
    Print("Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
    Print("Server: ", AccountInfoString(ACCOUNT_SERVER));
    Print("Broker: ", AccountInfoString(ACCOUNT_COMPANY));
    
    // Verifica connessione API
    TestAPIConnection();
    
    // Configura grafico
    SetupChart();
    
    // Timer per heartbeat
    EventSetTimer(HeartbeatInterval);
    
    if(EnableAutoTrading) {
        Print("✅ Esecuzione automatica ATTIVATA - In attesa di ordini dalla web-app");
    } else {
        Print("⚠️ Esecuzione automatica DISATTIVATA - Solo monitoraggio");
    }
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    EventKillTimer();
    Print("=== AI Cash-Revolution EA Disattivato ===");
    Print("Totale trade eseguiti: ", TotalTrades);
    Print("Profitto totale: $", DoubleToString(TotalProfit, 2));
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Aggiorna status display
    UpdateDisplay();
    
    // Gestisci trade aperti
    ManageOpenTrades();
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer() {
    // Invia heartbeat e controlla ordini pendenti
    if(TimeCurrent() - LastHeartbeat >= HeartbeatInterval) {
        SendHeartbeat();
        CheckPendingOrders();
        LastHeartbeat = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Genera ID unico per l'EA                                        |
//+------------------------------------------------------------------+
void GenerateUniqueID() {
    long account = AccountInfoInteger(ACCOUNT_LOGIN);
    string server = AccountInfoString(ACCOUNT_SERVER);
    datetime now = TimeCurrent();
    
    // Crea hash unico basato su account, server e timestamp
    UniqueID = "ACR_" + IntegerToString(account) + "_" + 
               StringSubstr(server, 0, 6) + "_" + 
               IntegerToString(now % 1000000);
               
    // Salva nelle variabili globali per la dashboard
    GlobalVariableSet("ACR_UniqueID", StringToDouble(UniqueID));
    
    Print("🔑 API Key generata: ", UniqueID);
    Print("📋 Copia questa chiave nella dashboard web!");
}

//+------------------------------------------------------------------+
//| Testa connessione API                                           |
//+------------------------------------------------------------------+
void TestAPIConnection() {
    string url = API_URL + "/mt5/bridge-status";
    string headers = "X-API-Key: " + UniqueID + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    char data[], result[];
    string result_headers;
    
    int timeout = 5000; // 5 secondi
    int res = WebRequest("GET", url, headers, timeout, data, result, result_headers);
    
    if(res == 200) {
        IsConnected = true;
        ConnectionStatus = "Connesso ✅";
        Print("✅ Connessione API riuscita!");
    } else {
        IsConnected = false;
        ConnectionStatus = "Errore connessione ❌";
        Print("❌ Errore connessione API. Codice: ", res);
        Print("URL: ", url);
    }
}

//+------------------------------------------------------------------+
//| Controlla ordini pendenti dal server web-app                    |
//+------------------------------------------------------------------+
void CheckPendingOrders() {
    if(!IsConnected) {
        TestAPIConnection();
        return;
    }
    
    string url = API_URL + "/mt5/pending-orders";
    string headers = "X-API-Key: " + API_KEY + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    char data[], result[];
    string result_headers;
    
    int res = WebRequest("GET", url, headers, 5000, data, result, result_headers);
    
    if(res == 200) {
        string response = CharArrayToString(result);
        ProcessPendingOrders(response);
    } else {
        Print("⚠️ Errore controllo ordini pendenti. Codice: ", res);
        IsConnected = false;
        ConnectionStatus = "Disconnesso ⚠️";
    }
}

//+------------------------------------------------------------------+
//| Processa ordini pendenti dal server web-app                     |
//+------------------------------------------------------------------+
void ProcessPendingOrders(string response) {
    // Parse JSON response (semplificato)
    if(StringFind(response, "\"status\":\"success\"") < 0) {
        return;
    }
    
    // Controlla se ci sono ordini da eseguire
    if(StringFind(response, "\"orders\":[]") >= 0) {
        return; // Nessun ordine pendente
    }
    
    // Parse ordini pendenti (semplificato - in produzione usa libreria JSON)
    if(StringFind(response, "\"execute\":true") >= 0) {
        // Estrai dati ordine dal JSON
        string symbol = ExtractJsonValue(response, "symbol");
        string orderType = ExtractJsonValue(response, "type");  
        double volume = StringToDouble(ExtractJsonValue(response, "volume"));
        double entryPrice = StringToDouble(ExtractJsonValue(response, "entry_price"));
        double stopLoss = StringToDouble(ExtractJsonValue(response, "stop_loss"));
        double takeProfit = StringToDouble(ExtractJsonValue(response, "take_profit"));
        string orderId = ExtractJsonValue(response, "order_id");
        int confidence = (int)StringToInteger(ExtractJsonValue(response, "confidence"));
        
        // Crea struttura segnale
        Signal signal;
        signal.symbol = symbol;
        signal.type = (orderType == "BUY") ? 0 : 1;
        signal.entry_price = entryPrice;
        signal.stop_loss = stopLoss;
        signal.take_profit = takeProfit;
        signal.lot_size = volume;
        signal.confidence = confidence;
        signal.explanation = "Ordine da web-app ID: " + orderId + " (Confidenza: " + IntegerToString(confidence) + "%)";
        signal.timestamp = TimeCurrent();
        signal.executed = false;
        
        // Controlla confidenza minima
        if(confidence < MinConfidencePercent) {
            Print("⚠️ Segnale ignorato - Confidenza ", confidence, "% < minimo ", MinConfidencePercent, "%");
            ConfirmOrderExecution(orderId, false);
            return;
        }
        
        // Esegui l'ordine se auto-trading è attivo e confidenza è sufficiente
        if(EnableAutoTrading && IsValidTradingTime()) {
            Print("✅ Eseguendo segnale con confidenza ", confidence, "% >= ", MinConfidencePercent, "%");
            if(ExecuteSignal(signal)) {
                // Notifica al server che l'ordine è stato eseguito
                ConfirmOrderExecution(orderId, true);
            } else {
                ConfirmOrderExecution(orderId, false);
            }
        } else {
            string reason = !EnableAutoTrading ? "auto-trading disattivato" : "orario trading non valido";
            Print("⚠️ Ordine ricevuto ma ", reason);
            ConfirmOrderExecution(orderId, false);
        }
    }
}

//+------------------------------------------------------------------+
//| Estrae valore da JSON (funzione semplificata)                   |
//+------------------------------------------------------------------+
string ExtractJsonValue(string json, string key) {
    string searchStr = "\"" + key + "\":\"";
    int startPos = StringFind(json, searchStr);
    if(startPos < 0) {
        // Prova con valore numerico
        searchStr = "\"" + key + "\":";
        startPos = StringFind(json, searchStr);
        if(startPos < 0) return "";
        startPos += StringLen(searchStr);
        int endPos = StringFind(json, ",", startPos);
        if(endPos < 0) endPos = StringFind(json, "}", startPos);
        return StringSubstr(json, startPos, endPos - startPos);
    }
    
    startPos += StringLen(searchStr);
    int endPos = StringFind(json, "\"", startPos);
    if(endPos < 0) return "";
    
    return StringSubstr(json, startPos, endPos - startPos);
}

//+------------------------------------------------------------------+
//| Conferma esecuzione ordine al server                            |
//+------------------------------------------------------------------+
void ConfirmOrderExecution(string orderId, bool success) {
    string url = API_URL + "/mt5/order-execution";
    string headers = "X-API-Key: " + API_KEY + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    string json = "{";
    json += "\"order_id\":\"" + orderId + "\",";
    json += "\"executed\":" + (success ? "true" : "false") + ",";
    json += "\"timestamp\":" + IntegerToString(TimeCurrent()) + ",";
    json += "\"ea_version\":\"2.0\"";
    json += "}";
    
    char data[];
    StringToCharArray(json, data, 0, StringLen(json));
    
    char result[];
    string result_headers;
    
    int res = WebRequest("POST", url, headers, 5000, data, result, result_headers);
    
    if(res == 200) {
        Print("✅ Conferma esecuzione inviata per ordine ", orderId);
    } else {
        Print("❌ Errore invio conferma per ordine ", orderId, ". Codice: ", res);
    }
}

//+------------------------------------------------------------------+
//| Esegue un segnale di trading                                    |
//+------------------------------------------------------------------+
bool ExecuteSignal(Signal &signal) {
    // Controlla condizioni per il trading
    if(!IsTradeAllowed()) {
        return false;
    }
    
    MqlTradeRequest request;
    MqlTradeResult result;
    
    ZeroMemory(request);
    
    request.action = TRADE_ACTION_DEAL;
    request.symbol = signal.symbol;
    request.volume = signal.lot_size;
    request.type = (signal.type == 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    request.price = signal.entry_price;
    request.sl = EnableStopLoss ? signal.stop_loss : 0;
    request.tp = EnableTakeProfit ? signal.take_profit : 0;
    request.deviation = Slippage;
    request.magic = MagicNumber;
    request.comment = "AI-Signal-" + IntegerToString(signal.confidence) + "%";
    request.type_filling = ORDER_FILLING_IOC;
    
    if(OrderSend(request, result)) {
        TotalTrades++;
        signal.executed = true;
        
        Print("✅ Segnale eseguito: ", signal.symbol, " ", 
              (signal.type == 0 ? "BUY" : "SELL"), " Lotto: ", signal.lot_size, 
              " Confidenza: ", signal.confidence, "%");
        Print("💡 Spiegazione: ", signal.explanation);
        
        if(SendNotifications) {
            SendNotification("✅ Trade aperto: " + signal.symbol + " " + 
                           (signal.type == 0 ? "BUY" : "SELL") + 
                           " | Confidenza: " + IntegerToString(signal.confidence) + "%");
        }
        
        // Invia conferma al server
        SendTradeConfirmation(result.order, signal);
        
        return true;
        
    } else {
        Print("❌ Errore esecuzione trade: ", result.retcode, " - ", result.comment);
        return false;
    }
}

//+------------------------------------------------------------------+
//| Calcola lotto ottimale basato su gestione rischio               |
//+------------------------------------------------------------------+
double CalculateOptimalLotSize() {
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = balance * (MaxRiskPercent / 100.0);
    
    // Calcola lotto basato su rischio (semplificato)
    double lotSize = NormalizeDouble(riskAmount / 1000.0, 2);
    
    // Applica limiti
    if(lotSize > MaxLotSize) lotSize = MaxLotSize;
    if(lotSize < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)) {
        lotSize = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    }
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Controlla se il trading è permesso                              |
//+------------------------------------------------------------------+
bool IsTradeAllowed() {
    // Controlla numero massimo di trade
    if(GetOpenTradesCount() >= MaxSimultaneousTrades) {
        return false;
    }
    
    // Controlla orari di trading
    if(!IsValidTradingTime()) {
        return false;
    }
    
    // Controlla se il mercato è aperto
    if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE)) {
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Conta trade aperti con questo Magic Number                      |
//+------------------------------------------------------------------+
int GetOpenTradesCount() {
    int count = 0;
    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionSelectByIndex(i)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                count++;
            }
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Controlla orari di trading validi                               |
//+------------------------------------------------------------------+
bool IsValidTradingTime() {
    if(!EnableTradingHours) return true;
    
    MqlDateTime dt;
    TimeCurrent(dt);
    
    return (dt.hour >= StartHour && dt.hour < EndHour);
}

//+------------------------------------------------------------------+
//| Gestisce trade aperti                                           |
//+------------------------------------------------------------------+
void ManageOpenTrades() {
    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionSelectByIndex(i)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                // Aggiorna statistiche
                double currentProfit = PositionGetDouble(POSITION_PROFIT);
                // Qui puoi aggiungere logica di trailing stop, break-even, etc.
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Invia heartbeat al server                                       |
//+------------------------------------------------------------------+
void SendHeartbeat() {
    string url = API_URL + "/mt5/heartbeat";
    string headers = "X-API-Key: " + UniqueID + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    // Costruisci JSON con stats account
    string json = "{";
    json += "\"account\":\"" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "\",";
    json += "\"server\":\"" + AccountInfoString(ACCOUNT_SERVER) + "\",";
    json += "\"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + ",";
    json += "\"equity\":" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + ",";
    json += "\"margin\":" + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_FREE), 2) + ",";
    json += "\"trades\":" + IntegerToString(GetOpenTradesCount()) + ",";
    json += "\"timestamp\":" + IntegerToString(TimeCurrent());
    json += "}";
    
    char data[];
    StringToCharArray(json, data, 0, StringLen(json));
    
    char result[];
    string result_headers;
    
    WebRequest("POST", url, headers, 5000, data, result, result_headers);
}

//+------------------------------------------------------------------+
//| Invia conferma trade al server                                  |
//+------------------------------------------------------------------+
void SendTradeConfirmation(ulong ticket, Signal &signal) {
    string url = API_URL + "/mt5/trade-confirmation";
    string headers = "X-API-Key: " + UniqueID + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    string json = "{";
    json += "\"ticket\":\"" + IntegerToString(ticket) + "\",";
    json += "\"symbol\":\"" + signal.symbol + "\",";
    json += "\"type\":" + IntegerToString(signal.type) + ",";
    json += "\"volume\":" + DoubleToString(signal.lot_size, 2) + ",";
    json += "\"price\":" + DoubleToString(signal.entry_price, 5) + ",";
    json += "\"sl\":" + DoubleToString(signal.stop_loss, 5) + ",";
    json += "\"tp\":" + DoubleToString(signal.take_profit, 5) + ",";
    json += "\"timestamp\":" + IntegerToString(TimeCurrent());
    json += "}";
    
    char data[];
    StringToCharArray(json, data, 0, StringLen(json));
    
    char result[];
    string result_headers;
    
    WebRequest("POST", url, headers, 5000, data, result, result_headers);
}

//+------------------------------------------------------------------+
//| Setup grafico con info EA                                       |
//+------------------------------------------------------------------+
void SetupChart() {
    // Configura proprietà grafico
    ChartSetInteger(0, CHART_SHOW_GRID, false);
    ChartSetInteger(0, CHART_SHOW_PERIOD_SEP, true);
    
    // Aggiungi etichette informative
    ObjectCreate(0, "ACR_Label", OBJ_LABEL, 0, 0, 0);
    ObjectSetInteger(0, "ACR_Label", OBJPROP_XDISTANCE, 10);
    ObjectSetInteger(0, "ACR_Label", OBJPROP_YDISTANCE, 30);
    ObjectSetString(0, "ACR_Label", OBJPROP_TEXT, "AI Cash-Revolution EA v2.0");
    ObjectSetInteger(0, "ACR_Label", OBJPROP_COLOR, clrLimeGreen);
    ObjectSetInteger(0, "ACR_Label", OBJPROP_FONTSIZE, 10);
}

//+------------------------------------------------------------------+
//| Aggiorna display informazioni                                   |
//+------------------------------------------------------------------+
void UpdateDisplay() {
    static datetime lastUpdate = 0;
    
    // Aggiorna ogni 5 secondi
    if(TimeCurrent() - lastUpdate < 5) return;
    lastUpdate = TimeCurrent();
    
    // Aggiorna label con info attuali
    string info = "AI Cash-Revolution EA v2.0\n";
    info += "Status: " + ConnectionStatus + "\n";
    info += "API Key: " + UniqueID + "\n";
    info += "Trade aperti: " + IntegerToString(GetOpenTradesCount()) + "/" + IntegerToString(MaxSimultaneousTrades) + "\n";
    info += "Profit oggi: $" + DoubleToString(GetTodaysProfit(), 2);
    
    ObjectSetString(0, "ACR_Label", OBJPROP_TEXT, info);
    
    // Cambia colore in base alla connessione
    color labelColor = IsConnected ? clrLimeGreen : clrRed;
    ObjectSetInteger(0, "ACR_Label", OBJPROP_COLOR, labelColor);
}

//+------------------------------------------------------------------+
//| Calcola profit di oggi                                          |
//+------------------------------------------------------------------+
double GetTodaysProfit() {
    double todaysProfit = 0.0;
    datetime startOfDay = (TimeCurrent() / 86400) * 86400; // Inizio giornata
    
    // Somma profit da deal history di oggi
    HistorySelect(startOfDay, TimeCurrent());
    for(int i = 0; i < HistoryDealsTotal(); i++) {
        ulong ticket = HistoryDealGetTicket(i);
        if(HistoryDealGetInteger(ticket, DEAL_MAGIC) == MagicNumber) {
            todaysProfit += HistoryDealGetDouble(ticket, DEAL_PROFIT);
        }
    }
    
    // Aggiungi profit non realizzato
    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionSelectByIndex(i)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                todaysProfit += PositionGetDouble(POSITION_PROFIT);
            }
        }
    }
    
    return todaysProfit;
}

//+------------------------------------------------------------------+
//| Event handler per nuovi trade                                   |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result) {
    // Gestisci eventi trade per statistiche
    if(trans.type == TRADE_TRANSACTION_DEAL_ADD) {
        if(HistoryDealSelect(trans.deal)) {
            if(HistoryDealGetInteger(trans.deal, DEAL_MAGIC) == MagicNumber) {
                double profit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT);
                TotalProfit += profit;
                
                if(EnableTradeLog) {
                    Print("💰 Trade chiuso. Profit: $", DoubleToString(profit, 2));
                    Print("💎 Profit totale EA: $", DoubleToString(TotalProfit, 2));
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Gestisce eventi di input utente                                 |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam) {
    // Qui puoi aggiungere controlli per pulsanti sulla chart, etc.
    if(id == CHARTEVENT_OBJECT_CLICK) {
        if(sparam == "ACR_Button_Refresh") {
            TestAPIConnection();
            CheckForNewSignals();
        }
    }
}

//+------------------------------------------------------------------+
//| Funzioni helper per notifiche                                   |
//+------------------------------------------------------------------+
void SendNotification(string message) {
    if(!SendNotifications) return;
    
    // Invia notifica push
    SendNotification(message);
    
    // Log nel terminale  
    Print("📱 ", message);
}