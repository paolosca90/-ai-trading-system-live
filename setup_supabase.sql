-- SQL script per creare le tabelle in Supabase
-- Esegui questo nel SQL Editor di Supabase

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    subscription_plan VARCHAR(50),
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella segnali trading
CREATE TABLE IF NOT EXISTS trading_signals (
    id VARCHAR(50) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price DECIMAL(10,5) NOT NULL,
    stop_loss DECIMAL(10,5) NOT NULL,
    take_profit DECIMAL(10,5) NOT NULL,
    confidence INTEGER,
    rationale TEXT,
    timeframe VARCHAR(10) DEFAULT 'H1',
    ai_model VARCHAR(100) DEFAULT 'AI-Generator',
    status VARCHAR(20) DEFAULT 'pending',
    risk_reward_ratio DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella trades eseguiti
CREATE TABLE IF NOT EXISTS trades (
    id VARCHAR(50) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    signal_id VARCHAR(50) REFERENCES trading_signals(id),
    mt5_trade_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    volume DECIMAL(6,2) NOT NULL,
    entry_price DECIMAL(10,5) NOT NULL,
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),
    close_price DECIMAL(10,5),
    profit DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    demo_mode BOOLEAN DEFAULT TRUE,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_signals_user_id ON trading_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON trading_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_signal_id ON trades(signal_id);

-- Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Policies per sicurezza
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (id = auth.uid());
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (id = auth.uid());
CREATE POLICY "Users can view own signals" ON trading_signals FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can view own trades" ON trades FOR SELECT USING (user_id = auth.uid());

-- Inserisci alcuni segnali di esempio
INSERT INTO trading_signals (id, symbol, direction, entry_price, stop_loss, take_profit, confidence, rationale, status) VALUES
('DEMO001', 'EURUSD', 'BUY', 1.0842, 1.0820, 1.0880, 87, 'RSI oversold + Support level + EUR strength', 'pending'),
('DEMO002', 'GBPUSD', 'SELL', 1.2645, 1.2670, 1.2600, 92, 'Resistance breakout failure + GBP weakness', 'pending'),
('DEMO003', 'ES', 'BUY', 5485.50, 5470.00, 5520.00, 84, 'Bullish pattern + Volume confirmation', 'pending')
ON CONFLICT (id) DO NOTHING;