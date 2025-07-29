# Sophisticated Trading Platform with Multiple Inheritance

from datetime import datetime, date
from typing import Dict, List, Any, Union
import random

class TradingAccount:
    """Base class for trading account management"""
    
    def __init__(self, account_id: str, name: str, initial_balance: float):
        self.account_id = account_id
        self.name = name
        self.balance = initial_balance
        self.portfolio = {}  # {symbol: quantity}
        self.transaction_history = []
        self.created_date = date.today()
    
    def deposit(self, amount: float) -> bool:
        """Deposit money into the account"""
        if amount > 0:
            self.balance += amount
            self.transaction_history.append({
                "type": "deposit",
                "amount": amount,
                "timestamp": datetime.now(),
                "balance_after": self.balance
            })
            return True
        return False
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account"""
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append({
                "type": "withdrawal",
                "amount": amount,
                "timestamp": datetime.now(),
                "balance_after": self.balance
            })
            return True
        return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return {
            "account_id": self.account_id,
            "name": self.name,
            "balance": self.balance,
            "portfolio": self.portfolio,
            "created_date": self.created_date
        }
    
    def buy_asset(self, symbol: str, quantity: int, price: float) -> bool:
        """Buy an asset"""
        total_cost = quantity * price
        if total_cost <= self.balance:
            self.balance -= total_cost
            if symbol in self.portfolio:
                self.portfolio[symbol] += quantity
            else:
                self.portfolio[symbol] = quantity
            
            self.transaction_history.append({
                "type": "buy",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_cost": total_cost,
                "timestamp": datetime.now()
            })
            return True
        return False
    
    def sell_asset(self, symbol: str, quantity: int, price: float) -> bool:
        """Sell an asset"""
        if symbol in self.portfolio and self.portfolio[symbol] >= quantity:
            total_value = quantity * price
            self.balance += total_value
            self.portfolio[symbol] -= quantity
            
            if self.portfolio[symbol] == 0:
                del self.portfolio[symbol]
            
            self.transaction_history.append({
                "type": "sell",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_value": total_value,
                "timestamp": datetime.now()
            })
            return True
        return False


class RiskManagement:
    """Risk assessment and management capabilities"""
    
    def __init__(self):
        self.risk_parameters = {
            "max_position_size": 0.1,  # 10% of portfolio
            "max_daily_loss": 0.05,    # 5% daily loss limit
            "diversification_limit": 0.3  # Max 30% in single asset
        }
    
    def assess_portfolio_risk(self) -> str:
        """Assess overall portfolio risk level"""
        if not hasattr(self, 'portfolio') or not self.portfolio:
            return "Low"
        
        # Simple risk assessment based on portfolio concentration
        total_positions = len(self.portfolio)
        
        if total_positions >= 10:
            return "Low"
        elif total_positions >= 5:
            return "Medium"
        else:
            return "High"
    
    def calculate_position_size(self, symbol: str, price: float) -> int:
        """Calculate optimal position size based on risk parameters"""
        if not hasattr(self, 'balance'):
            return 0
        
        max_investment = self.balance * self.risk_parameters["max_position_size"]
        position_size = int(max_investment / price)
        return max(0, position_size)
    
    def validate_trade(self, symbol: str, quantity: int, price: float, trade_type: str) -> bool:
        """Validate if trade meets risk criteria"""
        if trade_type == "buy":
            total_cost = quantity * price
            if not hasattr(self, 'balance'):
                return False
            
            # Check if trade exceeds balance
            if total_cost > self.balance:
                return False
            
            # Check position size limits
            max_investment = self.balance * self.risk_parameters["max_position_size"]
            if total_cost > max_investment:
                return False
        
        elif trade_type == "sell":
            if not hasattr(self, 'portfolio'):
                return False
            
            # Check if we have enough assets to sell
            if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
                return False
        
        return True


class AnalyticsEngine:
    """Market analysis and analytics capabilities"""
    
    def __init__(self):
        self.market_data_cache = {}
        self.analysis_history = []
    
    def analyze_market_trend(self, symbol: str) -> Dict[str, Any]:
        """Analyze market trend for a given symbol"""
        # Simulate market analysis
        trends = ["bullish", "bearish", "sideways"]
        confidence_levels = [0.6, 0.7, 0.8, 0.9]
        
        analysis = {
            "symbol": symbol,
            "trend": random.choice(trends),
            "confidence": random.choice(confidence_levels),
            "support_level": round(random.uniform(100, 150), 2),
            "resistance_level": round(random.uniform(150, 200), 2),
            "timestamp": datetime.now()
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    def calculate_portfolio_performance(self) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        if not hasattr(self, 'transaction_history') or not self.transaction_history:
            return {
                "total_return": 0.0,
                "percentage_return": 0.0,
                "number_of_trades": 0
            }
        
        # Simulate performance calculation
        total_trades = len([t for t in self.transaction_history if t.get("type") in ["buy", "sell"]])
        
        return {
            "total_return": round(random.uniform(-1000, 5000), 2),
            "percentage_return": round(random.uniform(-10, 25), 2),
            "number_of_trades": total_trades
        }
    
    def get_market_indicators(self, symbol: str) -> Dict[str, float]:
        """Get technical indicators for a symbol"""
        return {
            "rsi": round(random.uniform(20, 80), 2),
            "macd": round(random.uniform(-1, 1), 3),
            "bollinger_bands": {
                "upper": round(random.uniform(180, 200), 2),
                "middle": round(random.uniform(150, 180), 2),
                "lower": round(random.uniform(120, 150), 2)
            }
        }


class NotificationSystem:
    """Alert and notification functionality"""
    
    def __init__(self):
        self.price_alerts = {}  # {symbol: [alerts]}
        self.notifications = []
        self.notification_settings = {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True
        }
    
    def set_price_alert(self, symbol: str, target_price: float, condition: str) -> bool:
        """Set a price alert for a symbol"""
        if condition not in ["above", "below"]:
            return False
        
        alert = {
            "symbol": symbol,
            "target_price": target_price,
            "condition": condition,
            "created_at": datetime.now(),
            "active": True
        }
        
        if symbol not in self.price_alerts:
            self.price_alerts[symbol] = []
        
        self.price_alerts[symbol].append(alert)
        return True
    
    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """Get all pending notifications"""
        return [n for n in self.notifications if n.get("status") == "pending"]
    
    def send_notification(self, message: str, priority: str = "medium") -> bool:
        """Send a notification"""
        notification = {
            "message": message,
            "priority": priority,
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        self.notifications.append(notification)
        return True
    
    def check_price_alerts(self, symbol: str, current_price: float) -> List[str]:
        """Check if any price alerts are triggered"""
        triggered_alerts = []
        
        if symbol in self.price_alerts:
            for alert in self.price_alerts[symbol]:
                if alert["active"]:
                    if (alert["condition"] == "above" and current_price >= alert["target_price"]) or \
                       (alert["condition"] == "below" and current_price <= alert["target_price"]):
                        message = f"Price alert: {symbol} is {alert['condition']} {alert['target_price']}"
                        triggered_alerts.append(message)
                        alert["active"] = False
                        self.send_notification(message, "high")
        
        return triggered_alerts


class StockTrader(TradingAccount, RiskManagement, AnalyticsEngine):
    """Stock trading with risk management and analytics"""
    
    def __init__(self, account_id: str, name: str, initial_balance: float):
        TradingAccount.__init__(self, account_id, name, initial_balance)
        RiskManagement.__init__(self)
        AnalyticsEngine.__init__(self)
        self.trader_type = "stock"
        self.commission_rate = 0.001  # 0.1% commission
    
    def execute_trade(self, symbol: str, quantity: int, price: float, trade_type: str) -> bool:
        """Execute a stock trade with risk validation"""
        # Validate trade using risk management
        if not self.validate_trade(symbol, quantity, price, trade_type):
            return False
        
        # Execute trade
        if trade_type == "buy":
            total_cost = quantity * price * (1 + self.commission_rate)
            if total_cost <= self.balance:
                return self.buy_asset(symbol, quantity, price)
        elif trade_type == "sell":
            return self.sell_asset(symbol, quantity, price)
        
        return False
    
    def get_stock_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock analysis"""
        market_trend = self.analyze_market_trend(symbol)
        indicators = self.get_market_indicators(symbol)
        
        return {
            "market_trend": market_trend,
            "technical_indicators": indicators,
            "risk_assessment": self.assess_portfolio_risk()
        }


class CryptoTrader(TradingAccount, RiskManagement, NotificationSystem):
    """Cryptocurrency trading with risk management and notifications"""
    
    def __init__(self, account_id: str, name: str, initial_balance: float):
        TradingAccount.__init__(self, account_id, name, initial_balance)
        RiskManagement.__init__(self)
        NotificationSystem.__init__(self)
        self.trader_type = "crypto"
        self.trading_fee = 0.0025  # 0.25% trading fee
    
    def execute_crypto_trade(self, symbol: str, quantity: float, price: float, trade_type: str) -> bool:
        """Execute a cryptocurrency trade"""
        # Crypto trades can have fractional quantities
        if trade_type == "buy":
            total_cost = quantity * price * (1 + self.trading_fee)
            if total_cost <= self.balance:
                self.balance -= total_cost
                if symbol in self.portfolio:
                    self.portfolio[symbol] += quantity
                else:
                    self.portfolio[symbol] = quantity
                
                # Send notification
                self.send_notification(f"Bought {quantity} {symbol} at ${price}")
                return True
        elif trade_type == "sell":
            if symbol in self.portfolio and self.portfolio[symbol] >= quantity:
                total_value = quantity * price * (1 - self.trading_fee)
                self.balance += total_value
                self.portfolio[symbol] -= quantity
                
                if self.portfolio[symbol] == 0:
                    del self.portfolio[symbol]
                
                # Send notification
                self.send_notification(f"Sold {quantity} {symbol} at ${price}")
                return True
        
        return False
    
    def monitor_crypto_prices(self, price_data: Dict[str, float]) -> List[str]:
        """Monitor cryptocurrency prices and trigger alerts"""
        all_alerts = []
        for symbol, price in price_data.items():
            alerts = self.check_price_alerts(symbol, price)
            all_alerts.extend(alerts)
        return all_alerts


class ProfessionalTrader(StockTrader, CryptoTrader):
    """Full-featured trader combining all capabilities"""
    
    def __init__(self, account_id: str, name: str, initial_balance: float):
        # Initialize both parent classes
        StockTrader.__init__(self, account_id, name, initial_balance)
        CryptoTrader.__init__(self, account_id, name, initial_balance)
        self.trader_type = "professional"
        self.premium_features = True
    
    def execute_diversified_strategy(self, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a diversified trading strategy across stocks and crypto"""
        results = {
            "status": "executed",
            "positions": [],
            "total_allocated": 0.0
        }
        
        stocks = strategy_config.get("stocks", [])
        crypto = strategy_config.get("crypto", [])
        allocation = strategy_config.get("allocation", {"stocks": 0.7, "crypto": 0.3})
        
        # Allocate funds
        stock_allocation = self.balance * allocation["stocks"]
        crypto_allocation = self.balance * allocation["crypto"]
        
        # Execute stock trades
        for stock in stocks:
            if stock_allocation > 0:
                # Simulate trade execution
                results["positions"].append({
                    "type": "stock",
                    "symbol": stock,
                    "allocated": stock_allocation / len(stocks)
                })
        
        # Execute crypto trades
        for coin in crypto:
            if crypto_allocation > 0:
                # Simulate trade execution
                results["positions"].append({
                    "type": "crypto",
                    "symbol": coin,
                    "allocated": crypto_allocation / len(crypto)
                })
        
        results["total_allocated"] = stock_allocation + crypto_allocation
        return results
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive trading report"""
        return {
            "account_info": self.get_account_info(),
            "portfolio_performance": self.calculate_portfolio_performance(),
            "risk_assessment": self.assess_portfolio_risk(),
            "pending_notifications": len(self.get_pending_notifications()),
            "trader_type": self.trader_type
        }


# === TESTING SECTION ===
if __name__ == "__main__":
    print("Testing Trading Platform with Multiple Inheritance")
    print("=" * 60)
    
    # Test Case 1: Multiple inheritance setup and MRO
    stock_trader = StockTrader("ST001", "John Doe", 50000.0)
    crypto_trader = CryptoTrader("CT001", "Jane Smith", 25000.0)
    pro_trader = ProfessionalTrader("PT001", "Mike Johnson", 100000.0)
    
    # Check Method Resolution Order
    mro_names = [cls.__name__ for cls in ProfessionalTrader.__mro__]
    assert "ProfessionalTrader" in mro_names
    assert "StockTrader" in mro_names
    assert "CryptoTrader" in mro_names
    
    # Test Case 2: Account management capabilities
    assert stock_trader.account_id == "ST001"
    assert stock_trader.balance == 50000.0
    
    deposit_result = stock_trader.deposit(10000)
    assert stock_trader.balance == 60000.0
    assert deposit_result == True
    
    withdrawal_result = stock_trader.withdraw(5000)
    assert stock_trader.balance == 55000.0
    
    # Test Case 3: Risk management functionality
    # Stock trader should have risk assessment
    risk_level = stock_trader.assess_portfolio_risk()
    assert risk_level in ["Low", "Medium", "High"]
    
    position_size = stock_trader.calculate_position_size("AAPL", 150.0)
    assert isinstance(position_size, int)
    assert position_size > 0
    
    # Test Case 4: Analytics capabilities
    # Stock trader has analytics through inheritance
    market_data = stock_trader.analyze_market_trend("AAPL")
    assert isinstance(market_data, dict)
    assert "trend" in market_data
    assert "confidence" in market_data
    
    # Test Case 5: Notification system for crypto trader
    # Crypto trader should have price alerts
    alert_set = crypto_trader.set_price_alert("BTC", 45000, "above")
    assert alert_set == True
    
    notifications = crypto_trader.get_pending_notifications()
    assert isinstance(notifications, list)
    
    # Test Case 6: Professional trader combining all features
    # Should have access to all inherited methods
    assert hasattr(pro_trader, 'assess_portfolio_risk')  # From RiskManagement
    assert hasattr(pro_trader, 'analyze_market_trend')   # From AnalyticsEngine
    assert hasattr(pro_trader, 'set_price_alert')       # From NotificationSystem
    
    # Execute complex trading strategy
    strategy_result = pro_trader.execute_diversified_strategy({
        "stocks": ["AAPL", "GOOGL"],
        "crypto": ["BTC", "ETH"],
        "allocation": {"stocks": 0.7, "crypto": 0.3}
    })
    assert strategy_result["status"] == "executed"
    assert len(strategy_result["positions"]) > 0
    
    print("All test cases passed successfully!")
    print("=" * 60)
    
    # Additional demonstration
    print("\nMethod Resolution Order for ProfessionalTrader:")
    for i, cls in enumerate(ProfessionalTrader.__mro__):
        print(f"{i+1}. {cls.__name__}")
    
    print(f"\nProfessionalTrader capabilities:")
    print(f"- Account ID: {pro_trader.account_id}")
    print(f"- Balance: ${pro_trader.balance:,.2f}")
    print(f"- Risk Assessment: {pro_trader.assess_portfolio_risk()}")
    print(f"- Has Analytics: {hasattr(pro_trader, 'analyze_market_trend')}")
    print(f"- Has Notifications: {hasattr(pro_trader, 'set_price_alert')}")
    
    print("\nTrading Platform Test Complete!")
