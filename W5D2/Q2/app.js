class StockChatApp {
    constructor() {
        // Initialize data from provided JSON
        this.stocks = [
            {"symbol": "AAPL", "price": 175.23, "change": 2.45, "changePercent": 1.42, "sentiment": "positive"},
            {"symbol": "GOOGL", "price": 127.85, "change": -1.23, "changePercent": -0.95, "sentiment": "negative"},
            {"symbol": "TSLA", "price": 248.91, "change": 5.67, "changePercent": 2.33, "sentiment": "positive"},
            {"symbol": "MSFT", "price": 378.42, "change": 0.89, "changePercent": 0.24, "sentiment": "neutral"},
            {"symbol": "AMZN", "price": 145.67, "change": -2.34, "changePercent": -1.58, "sentiment": "negative"}
        ];

        this.recommendations = [
            {"action": "BUY", "symbol": "AAPL", "reason": "Strong earnings momentum", "confidence": 85},
            {"action": "HOLD", "symbol": "TSLA", "reason": "Volatility expected", "confidence": 72},
            {"action": "WATCH", "symbol": "NVDA", "reason": "AI sector growth", "confidence": 88},
            {"action": "SELL", "symbol": "META", "reason": "Regulatory concerns", "confidence": 65}
        ];

        this.chatMessages = [
            {"user": "TradeMaster", "message": "AAPL looking strong after earnings! 📈", "timestamp": "10:23"},
            {"user": "MarketWatch", "message": "Anyone watching TSLA today? Big moves expected", "timestamp": "10:25"},
            {"user": "AnalystPro", "message": "Fed meeting tomorrow, expect volatility", "timestamp": "10:27"},
            {"user": "NewsBot", "message": "NEWS: Tech stocks rally on AI optimism", "timestamp": "10:28"},
            {"user": "ChartGuru", "message": "Support at $170 for AAPL holding well", "timestamp": "10:30"}
        ];

        this.news = [
            {"headline": "Apple reports strong Q4 earnings", "sentiment": "positive", "score": 0.85},
            {"headline": "Tesla faces production challenges", "sentiment": "negative", "score": -0.62},
            {"headline": "Microsoft Azure growth accelerates", "sentiment": "positive", "score": 0.73},
            {"headline": "Amazon logistics improvements", "sentiment": "neutral", "score": 0.15}
        ];

        this.metrics = {
            "activeUsers": 1247,
            "messagesPerMin": 34,
            "serverStatus": "Online",
            "latency": "45ms",
            "apiCalls": 2156
        };

        this.additionalMessages = [
            {"user": "CryptoKing", "message": "Volume picking up on tech stocks 📊", "timestamp": ""},
            {"user": "DayTrader99", "message": "RSI looking oversold on GOOGL", "timestamp": ""},
            {"user": "MarketMaven", "message": "Breaking: Fed hints at rate cut", "timestamp": ""},
            {"user": "TechAnalyst", "message": "NVDA breaking through resistance!", "timestamp": ""},
            {"user": "NewsAlert", "message": "🚨 NEWS: Major tech merger announced", "timestamp": ""},
            {"user": "StockGuru", "message": "Support levels holding strong", "timestamp": ""},
            {"user": "QuickTrade", "message": "Options flow showing bullish sentiment", "timestamp": ""},
            {"user": "MarketBeat", "message": "Sector rotation into growth stocks", "timestamp": ""}
        ];

        this.typingUsers = ["TradeMaster", "MarketWatch", "AnalystPro", "CryptoKing", "DayTrader99"];
        this.isTyping = false;
        this.currentTypingUser = null;

        this.init();
    }

    init() {
        this.renderInitialData();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    renderInitialData() {
        this.renderStocks();
        this.renderChatMessages();
        this.renderRecommendations();
        this.renderNews();
        this.renderMetrics();
    }

    renderStocks() {
        const stockList = document.getElementById('stockList');
        stockList.innerHTML = '';

        this.stocks.forEach(stock => {
            const stockItem = document.createElement('div');
            stockItem.className = 'stock-item';
            stockItem.dataset.symbol = stock.symbol;
            
            const changeClass = stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : 'neutral';
            const changeSign = stock.change > 0 ? '+' : '';
            
            stockItem.innerHTML = `
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-price-info">
                    <div class="stock-price">$${stock.price.toFixed(2)}</div>
                    <div class="stock-change ${changeClass}">
                        ${changeSign}$${Math.abs(stock.change).toFixed(2)} (${changeSign}${stock.changePercent.toFixed(2)}%)
                    </div>
                </div>
            `;
            
            stockItem.addEventListener('click', () => this.showStockModal(stock));
            stockList.appendChild(stockItem);
        });
    }

    renderChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';

        this.chatMessages.forEach(message => {
            this.addChatMessage(message, false);
        });
        
        this.scrollToBottom();
    }

    addChatMessage(message, animate = true) {
        const chatMessages = document.getElementById('chatMessages');
        
        // Ensure chatMessages element exists
        if (!chatMessages) {
            console.error('Chat messages container not found');
            return;
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        
        if (message.user === 'NewsBot' || message.user === 'NewsAlert' || message.user === 'MarketAlert') {
            messageElement.classList.add('news-alert');
        }

        const avatar = message.user.charAt(0).toUpperCase();
        const timestamp = message.timestamp || this.getCurrentTime();
        
        // Special styling for user's own messages
        const isOwnMessage = message.user === 'You';
        if (isOwnMessage) {
            messageElement.style.background = 'rgba(var(--color-primary-rgb, 33, 128, 141), 0.1)';
            messageElement.style.border = '1px solid rgba(var(--color-primary-rgb, 33, 128, 141), 0.3)';
        }
        
        messageElement.innerHTML = `
            <div class="message-avatar" style="${isOwnMessage ? 'background: var(--color-primary);' : ''}">${avatar}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-username" style="${isOwnMessage ? 'color: var(--color-primary);' : ''}">${message.user}</span>
                    <span class="message-timestamp">${timestamp}</span>
                </div>
                <p class="message-text">${message.message}</p>
            </div>
        `;

        if (!animate) {
            messageElement.style.animation = 'none';
        }

        chatMessages.appendChild(messageElement);
        
        // Always scroll to bottom when new message is added
        this.scrollToBottom();
        
        // Update metrics
        this.metrics.messagesPerMin += Math.floor(Math.random() * 3);
        this.updateMetricsDisplay();
    }

    renderRecommendations() {
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';

        this.recommendations.forEach(rec => {
            const recItem = document.createElement('div');
            recItem.className = 'recommendation-item';
            
            recItem.innerHTML = `
                <div class="recommendation-action ${rec.action.toLowerCase()}">${rec.action}</div>
                <div class="recommendation-details">
                    <div class="recommendation-symbol">${rec.symbol}</div>
                    <div class="recommendation-reason">${rec.reason}</div>
                </div>
                <div class="confidence-score">${rec.confidence}%</div>
            `;
            
            recommendationsList.appendChild(recItem);
        });
    }

    renderNews() {
        const newsList = document.getElementById('newsList');
        newsList.innerHTML = '';

        this.news.forEach(newsItem => {
            const newsElement = document.createElement('div');
            newsElement.className = `news-item ${newsItem.sentiment}`;
            
            const scoreText = newsItem.score > 0 ? `+${newsItem.score.toFixed(2)}` : newsItem.score.toFixed(2);
            
            newsElement.innerHTML = `
                <div class="news-headline">${newsItem.headline}</div>
                <div class="news-sentiment">
                    <span>Sentiment:</span>
                    <span class="sentiment-score">${scoreText}</span>
                </div>
            `;
            
            newsList.appendChild(newsElement);
        });
    }

    renderMetrics() {
        document.getElementById('activeUsers').textContent = this.metrics.activeUsers.toLocaleString();
        document.getElementById('messagesPerMin').textContent = this.metrics.messagesPerMin;
        document.getElementById('serverStatus').textContent = this.metrics.serverStatus;
        document.getElementById('latency').textContent = this.metrics.latency;
        document.getElementById('apiCalls').textContent = this.metrics.apiCalls.toLocaleString();
        document.getElementById('activeUsersCount').textContent = this.metrics.activeUsers.toLocaleString();
    }

    updateMetricsDisplay() {
        this.renderMetrics();
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const closeModal = document.getElementById('closeModal');
        const stockModal = document.getElementById('stockModal');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        closeModal.addEventListener('click', () => {
            stockModal.style.display = 'none';
        });

        stockModal.addEventListener('click', (e) => {
            if (e.target === stockModal) {
                stockModal.style.display = 'none';
            }
        });

        // Add escape key listener for modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && stockModal.style.display === 'flex') {
                stockModal.style.display = 'none';
            }
        });
    }

    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (message) {
            const newMessage = {
                user: 'You',
                message: message,
                timestamp: this.getCurrentTime()
            };
            
            // Add user's message immediately
            this.addChatMessage(newMessage, true);
            
            // Clear input field
            messageInput.value = '';
            
            // Focus back on input for continuous typing
            messageInput.focus();
            
            // Simulate response after a short delay
            setTimeout(() => {
                this.simulateResponse(message);
            }, 2000 + Math.random() * 3000);
        }
    }

    simulateResponse(originalMessage) {
        const responses = [
            "Great point! I'm seeing similar patterns.",
            "Thanks for sharing that insight!",
            "Agreed, that's what the charts are showing too.",
            "Interesting perspective on the market.",
            "I've been watching that as well.",
            "Good call on that one!",
            "The technicals support that view.",
            "Totally agree with that analysis.",
            "Nice catch! That's important to watch.",
            "Smart observation about the market."
        ];
        
        const randomUser = this.typingUsers[Math.floor(Math.random() * this.typingUsers.length)];
        const response = responses[Math.floor(Math.random() * responses.length)];
        
        this.showTypingIndicator(randomUser);
        
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addChatMessage({
                user: randomUser,
                message: response,
                timestamp: this.getCurrentTime()
            });
        }, 2000);
    }

    showStockModal(stock) {
        const modal = document.getElementById('stockModal');
        const modalSymbol = document.getElementById('modalStockSymbol');
        const modalPrice = document.getElementById('modalPrice');
        const modalChange = document.getElementById('modalChange');
        const stockInfo = document.getElementById('stockInfo');
        
        modalSymbol.textContent = stock.symbol;
        modalPrice.textContent = `$${stock.price.toFixed(2)}`;
        
        const changeSign = stock.change > 0 ? '+' : '';
        const changeClass = stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : 'neutral';
        modalChange.className = `price-change ${changeClass}`;
        modalChange.textContent = `${changeSign}$${Math.abs(stock.change).toFixed(2)} (${changeSign}${stock.changePercent.toFixed(2)}%)`;
        
        // Generate mock stock information
        const infos = {
            'AAPL': 'Apple Inc. continues to show strong performance with robust iPhone sales and services growth. Market cap: $2.8T. P/E Ratio: 28.5. Recent earnings beat expectations with strong guidance.',
            'GOOGL': 'Alphabet Inc. facing some headwinds but strong fundamentals in cloud and search. Market cap: $1.6T. P/E Ratio: 23.2. Cloud business showing accelerated growth.',
            'TSLA': 'Tesla Inc. showing volatility amid production scaling and competition. Market cap: $789B. P/E Ratio: 65.4. New model launches expected to drive growth.',
            'MSFT': 'Microsoft Corporation demonstrating steady growth with Azure and productivity suite. Market cap: $2.9T. P/E Ratio: 32.1. AI integration boosting product value.',
            'AMZN': 'Amazon.com Inc. focusing on operational efficiency and cloud growth. Market cap: $1.4T. P/E Ratio: 45.6. AWS continues to be a key growth driver.'
        };
        
        stockInfo.textContent = infos[stock.symbol] || 'Loading detailed stock information...';
        modal.style.display = 'flex';
    }

    showTypingIndicator(username) {
        if (this.isTyping) return;
        
        this.isTyping = true;
        this.currentTypingUser = username;
        const indicator = document.getElementById('typingIndicator');
        const userSpan = document.getElementById('typingUser');
        
        userSpan.textContent = username;
        indicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.currentTypingUser = null;
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = 'none';
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }
    }

    getCurrentTime() {
        const now = new Date();
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    updateStockPrices() {
        this.stocks.forEach(stock => {
            // Generate realistic price fluctuation (±0.1 to ±2.0)
            const fluctuation = (Math.random() - 0.5) * 4; // -2 to +2
            const percentChange = fluctuation / stock.price * 100;
            
            // Update price
            const oldPrice = stock.price;
            stock.price = Math.max(0.01, stock.price + fluctuation);
            stock.change = stock.price - (oldPrice - stock.change + fluctuation);
            stock.changePercent = (stock.change / (stock.price - stock.change)) * 100;
            
            // Update sentiment based on change
            if (stock.changePercent > 0.5) {
                stock.sentiment = 'positive';
            } else if (stock.changePercent < -0.5) {
                stock.sentiment = 'negative';
            } else {
                stock.sentiment = 'neutral';
            }
        });
        
        this.renderStocks();
        
        // Add flash effect to prices
        document.querySelectorAll('.stock-item').forEach(item => {
            item.classList.add('price-flash');
            setTimeout(() => item.classList.remove('price-flash'), 500);
        });
    }

    addRandomMessage() {
        if (this.additionalMessages.length === 0) {
            // Replenish messages if we run out
            this.additionalMessages = [
                {"user": "CryptoKing", "message": "Volume picking up on tech stocks 📊", "timestamp": ""},
                {"user": "DayTrader99", "message": "RSI looking oversold on GOOGL", "timestamp": ""},
                {"user": "MarketMaven", "message": "Breaking: Fed hints at rate cut", "timestamp": ""},
                {"user": "TechAnalyst", "message": "NVDA breaking through resistance!", "timestamp": ""},
                {"user": "QuickTrade", "message": "Options flow showing bullish sentiment", "timestamp": ""},
                {"user": "MarketBeat", "message": "Sector rotation into growth stocks", "timestamp": ""}
            ];
        }
        
        const messageIndex = Math.floor(Math.random() * this.additionalMessages.length);
        const message = this.additionalMessages[messageIndex];
        message.timestamp = this.getCurrentTime();
        
        // Show typing indicator first
        this.showTypingIndicator(message.user);
        
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addChatMessage(message);
            
            // Remove used message to avoid repetition
            this.additionalMessages.splice(messageIndex, 1);
        }, 1500 + Math.random() * 2000);
    }

    addNewsAlert() {
        const newsAlerts = [
            "🚨 BREAKING: Major tech earnings beat expectations",
            "📈 Market Update: S&P 500 reaches new highs",
            "⚡ Flash: Federal Reserve policy decision pending",
            "🔔 Alert: High volume detected in semiconductor stocks",
            "📊 Technical: Key resistance level broken on NASDAQ",
            "💡 Insight: AI sector showing strong momentum",
            "🎯 Focus: Energy stocks outperforming today",
            "📢 Update: Volatility index drops significantly",
            "🚀 Momentum: Growth stocks leading market rally"
        ];
        
        const alert = newsAlerts[Math.floor(Math.random() * newsAlerts.length)];
        
        this.addChatMessage({
            user: 'MarketAlert',
            message: alert,
            timestamp: this.getCurrentTime()
        });
    }

    updateRecommendations() {
        const actions = ['BUY', 'SELL', 'HOLD', 'WATCH'];
        const symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX'];
        const reasons = [
            'Strong earnings momentum',
            'Volatility expected', 
            'Technical breakout pattern',
            'Sector rotation play',
            'Oversold conditions',
            'Breaking resistance levels',
            'Fundamental improvements',
            'Market sentiment shift',
            'Analyst upgrades',
            'Strong institutional buying'
        ];
        
        // Update one random recommendation
        const index = Math.floor(Math.random() * this.recommendations.length);
        this.recommendations[index] = {
            action: actions[Math.floor(Math.random() * actions.length)],
            symbol: symbols[Math.floor(Math.random() * symbols.length)],
            reason: reasons[Math.floor(Math.random() * reasons.length)],
            confidence: 60 + Math.floor(Math.random() * 30)
        };
        
        this.renderRecommendations();
    }

    updateMetrics() {
        // Simulate realistic metric changes
        this.metrics.activeUsers += Math.floor(Math.random() * 20) - 10;
        this.metrics.activeUsers = Math.max(1000, this.metrics.activeUsers);
        
        this.metrics.apiCalls += Math.floor(Math.random() * 50) + 10;
        
        const latencyValue = 30 + Math.floor(Math.random() * 40);
        this.metrics.latency = `${latencyValue}ms`;
        
        this.updateMetricsDisplay();
    }

    startRealTimeUpdates() {
        // Stock price updates every 3-5 seconds
        setInterval(() => {
            this.updateStockPrices();
        }, 3000 + Math.random() * 2000);

        // Random chat messages every 10-30 seconds
        setInterval(() => {
            if (Math.random() > 0.3) { // 70% chance
                this.addRandomMessage();
            }
        }, 10000 + Math.random() * 20000);

        // News alerts every 1-2 minutes
        setInterval(() => {
            this.addNewsAlert();
        }, 60000 + Math.random() * 60000);

        // Recommendation updates every 30 seconds
        setInterval(() => {
            this.updateRecommendations();
        }, 30000);

        // Metrics updates every 10 seconds
        setInterval(() => {
            this.updateMetrics();
        }, 10000);

        // Connection status simulation
        setInterval(() => {
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            
            // Simulate occasional connection hiccups (rare)
            if (Math.random() > 0.98) {
                statusIndicator.classList.remove('online');
                statusText.textContent = 'Reconnecting...';
                
                setTimeout(() => {
                    statusIndicator.classList.add('online');
                    statusText.textContent = 'Connected';
                }, 2000);
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockChatApp();
});

// Handle page visibility change to pause updates when not visible
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('App paused - page not visible');
    } else {
        console.log('App resumed - page visible');
    }
});