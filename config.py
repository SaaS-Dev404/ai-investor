"""
AI Investor Platform Configuration
===================================
Default settings optimized from our research
"""

# Optimal stock/ETF selections
PRIMARY_STOCK = "VAS.AX"  # Vanguard Australian Shares ETF

# Approved backup stocks for auto-rebalance
BACKUP_STOCKS = [
    "BHP.AX",  # Defensive - mining
    "TLS.AX",  # Defensive - telco
    "WBC.AX",  # Defensive - banking
]

# Risk management settings (optimized from research)
TRAILING_STOP_PCT = 0.15      # 15% drawdown from peak
PROFIT_LOCK_PCT = 0.20        # 20% minimum gain before trailing activates

# Signal generation settings
BUY_SIGNAL_RSI_THRESHOLD = 35      # Buy when RSI < 35 (oversold)
BUY_SIGNAL_BB_THRESHOLD = 2        # Buy when price < 2 std deviations below BB

# Platform settings
MIN_CONTRIBUTION_WEEKLY = 5        # Minimum $5/week
MAX_TRADES_PER_YEAR = 10           # Cap to prevent overtrading

# Platform name
PLATFORM_NAME = "AI Investor"
PLATFORM_VERSION = "1.0.0"

# Authentication (set via environment variables in production)
# Use: export AUTH_USERNAME=youruser AUTH_PASSWORD=yourpass
import os
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'change-me-in-production')

# API Keys (to be configured by user)
# These would be set via environment variables in production
BROKER_API_KEY = None
BROKER_SECRET = None

print(f"✅ {PLATFORM_NAME} v{PLATFORM_VERSION} loaded")
print(f"   Primary: {PRIMARY_STOCK}")
print(f"   Backups: {BACKUP_STOCKS}")
print(f"   Risk: {TRAILING_STOP_PCT*100}% stop, {PROFIT_LOCK_PCT*100}% lock")
