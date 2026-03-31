"""
AI Trading Engine
=================
Core module that analyzes stocks and generates buy/sell signals
Based on our validated research from v1-v6 testing
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-investor')

import config


class StockAnalyzer:
    """Analyzes stocks and generates trading signals"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data = None
        self.signals = []
        
    def fetch_data(self, period: str = "1y"):
        """Fetch historical price data"""
        stock = yf.Ticker(self.ticker)
        self.data = stock.history(period=period)
        return self.data
    
    def calculate_indicators(self):
        """Calculate technical indicators"""
        df = self.data.copy()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Mid'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Mid'] - (bb_std * 2)
        
        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        self.data = df
        return df
    
    def generate_signal(self):
        """Generate current trading signal"""
        if self.data is None:
            self.fetch_data()
            self.calculate_indicators()
        
        latest = self.data.iloc[-1]
        
        # BUY signals
        buy_score = 0
        buy_reasons = []
        
        if latest['RSI'] < config.BUY_SIGNAL_RSI_THRESHOLD:
            buy_score += 2
            buy_reasons.append(f"Oversold (RSI: {latest['RSI']:.0f})")
        
        if latest['Close'] < latest['BB_Lower']:
            buy_score += 2
            buy_reasons.append("At lower Bollinger Band")
        
        # Golden cross forming
        if len(self.data) >= 3:
            if (latest['SMA_20'] > latest['SMA_50'] and 
                self.data.iloc[-3]['SMA_20'] <= self.data.iloc[-3]['SMA_50']):
                buy_score += 2
                buy_reasons.append("Golden cross forming")
        
        # SELL signals
        sell_score = 0
        sell_reasons = []
        
        if latest['RSI'] > 70:
            sell_score += 1
            sell_reasons.append(f"Overbought (RSI: {latest['RSI']:.0f})")
        
        # Trend broken
        if len(self.data) >= 5:
            prev_above = self.data.iloc[-5]['Close'] > self.data.iloc[-5]['SMA_50']
            now_below = latest['Close'] < latest['SMA_50']
            
            if prev_above and now_below:
                sell_score += 3
                sell_reasons.append("Trend breakdown")
        
        # Determine signal
        if buy_score >= 2:
            signal = "BUY"
            confidence = min(buy_score * 25, 100)
            reasons = buy_reasons
        elif sell_score >= 2:
            signal = "SELL"
            confidence = min(sell_score * 25, 100)
            reasons = sell_reasons
        else:
            signal = "HOLD"
            confidence = 50
            reasons = ["No clear signal"]
        
        return {
            'ticker': self.ticker,
            'signal': signal,
            'confidence': confidence,
            'price': float(latest['Close']),
            'rsi': float(latest['RSI']),
            'sma_20': float(latest['SMA_20']),
            'sma_50': float(latest['SMA_50']),
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_current_metrics(self):
        """Get current metrics"""
        if self.data is None:
            self.fetch_data()
            self.calculate_indicators()
        
        latest = self.data.iloc[-1]
        
        return {
            'price': float(latest['Close']),
            'rsi': float(latest['RSI']),
            'sma_20': float(latest['SMA_20']),
            'sma_50': float(latest['SMA_50']),
            'bb_lower': float(latest['BB_Lower']),
            'macd': float(latest['MACD']),
            'macd_hist': float(latest['MACD_Hist']),
            'volume': int(latest['Volume'])
        }


class PortfolioManager:
    """Manages portfolio positions"""
    
    def __init__(self, initial_capital: float = 0):
        self.cash = initial_capital
        self.position = 0
        self.buy_price = 0
        self.peak_price = 0
        self.position_ticker = None
        
    def buy(self, ticker: str, price: float, cash_available: float):
        """Execute buy"""
        if cash_available < price:
            return {'success': False, 'reason': 'Insufficient funds'}
        
        shares = cash_available / price
        self.position = shares
        self.buy_price = price
        self.peak_price = price
        self.cash = 0
        self.position_ticker = ticker
        
        return {
            'success': True,
            'ticker': ticker,
            'shares': shares,
            'price': price,
            'total': cash_available
        }
    
    def sell(self, price: float):
        """Execute sell"""
        if self.position == 0:
            return {'success': False, 'reason': 'No position'}
        
        proceeds = self.position * price
        profit_pct = (price - self.buy_price) / self.buy_price * 100
        
        self.cash = proceeds
        self.position = 0
        self.position_ticker = None
        
        return {
            'success': True,
            'shares': self.position,
            'price': price,
            'proceeds': proceeds,
            'profit_pct': profit_pct
        }
    
    def check_trailing_stop(self, current_price: float):
        """Check trailing stop"""
        if self.position == 0:
            return {'triggered': False}
        
        self.peak_price = max(self.peak_price, current_price)
        drawdown = (self.peak_price - current_price) / self.peak_price
        gain = (current_price - self.buy_price) / self.buy_price
        
        should_sell = (drawdown >= config.TRAILING_STOP_PCT and 
                       gain >= config.PROFIT_LOCK_PCT)
        
        return {
            'triggered': should_sell,
            'drawdown': drawdown,
            'gain': gain,
            'peak_price': self.peak_price
        }
    
    def get_status(self, current_price: float = 0):
        """Get portfolio status"""
        pos_val = self.position * current_price if current_price > 0 else 0
        
        return {
            'cash': self.cash,
            'position': self.position,
            'position_value': pos_val,
            'total_value': pos_val + self.cash,
            'current_ticker': self.position_ticker,
            'buy_price': self.buy_price,
            'unrealized_pct': ((current_price - self.buy_price) / self.buy_price * 100) 
                             if self.position > 0 and current_price > 0 else 0
        }


def analyze_portfolio(tickers: list):
    """Analyze multiple stocks"""
    results = []
    
    for ticker in tickers:
        try:
            analyzer = StockAnalyzer(ticker)
            signal = analyzer.generate_signal()
            results.append(signal)
        except Exception as e:
            results.append({'ticker': ticker, 'signal': 'ERROR', 'error': str(e)})
    
    return results


if __name__ == "__main__":
    print("="*60)
    print("AI Trading Engine")
    print("="*60)
    
    all_stocks = [config.PRIMARY_STOCK] + config.BACKUP_STOCKS
    results = analyze_portfolio(all_stocks)
    
    for r in results:
        print(f"\n{r['ticker']}: {r['signal']} ({r['confidence']}%)")
        print(f"  ${r['price']:.2f} | RSI: {r['rsi']:.0f}")
        print(f"  {', '.join(r['reasons'])}")
