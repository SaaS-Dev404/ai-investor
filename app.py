"""
AI Investor Platform
====================
Main application entry point
"""

from flask import Flask, render_template, jsonify, request
from functools import wraps
import hashlib
import hmac
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-investor')

import config
from core.trading_engine import StockAnalyzer, PortfolioManager, analyze_portfolio

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['SECRET_KEY'] = config.AUTH_PASSWORD


def require_auth(f):
    """Decorator to require Basic Auth for all routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def check_auth(username, password):
    """Verify credentials - supports both plain and hashed"""
    # Simple comparison (in production, use proper hashing)
    return (username == config.AUTH_USERNAME and 
            hmac.compare_digest(password, config.AUTH_PASSWORD))

# Initialize portfolio manager
portfolio = PortfolioManager(initial_capital=0)


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/signals')
@require_auth
def get_signals():
    """Get current trading signals"""
    all_stocks = [config.PRIMARY_STOCK] + config.BACKUP_STOCKS
    signals = analyze_portfolio(all_stocks)
    return jsonify(signals)


@app.route('/api/portfolio')
@require_auth
def get_portfolio():
    """Get current portfolio status"""
    # Get current price of position ticker
    current_price = 0
    if portfolio.position_ticker:
        try:
            analyzer = StockAnalyzer(portfolio.position_ticker)
            analyzer.fetch_data()
            current_price = analyzer.data.iloc[-1]['Close']
        except:
            pass
    
    status = portfolio.get_status(current_price)
    return jsonify(status)


@app.route('/api/buy', methods=['POST'])
@require_auth
def execute_buy():
    """Execute a buy order"""
    data = request.json
    ticker = data.get('ticker')
    
    try:
        analyzer = StockAnalyzer(ticker)
        analyzer.fetch_data()
        price = analyzer.data.iloc[-1]['Close']
        
        result = portfolio.buy(ticker, price, portfolio.cash + 10000)  # Assume user has cash
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sell', methods=['POST'])
@require_auth
def execute_sell():
    """Execute a sell order"""
    try:
        analyzer = StockAnalyzer(portfolio.position_ticker)
        analyzer.fetch_data()
        price = analyzer.data.iloc[-1]['Close']
        
        result = portfolio.sell(price)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config')
@require_auth
def get_config():
    """Get platform configuration"""
    return jsonify({
        'primary_stock': config.PRIMARY_STOCK,
        'backup_stocks': config.BACKUP_STOCKS,
        'trailing_stop_pct': config.TRAILING_STOP_PCT,
        'profit_lock_pct': config.PROFIT_LOCK_PCT,
        'min_contribution': config.MIN_CONTRIBUTION_WEEKLY
    })


if __name__ == '__main__':
    print(f"\n🚀 Starting {config.PLATFORM_NAME}")
    print(f"   Primary: {config.PRIMARY_STOCK}")
    print(f"   Backups: {config.BACKUP_STOCKS}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
