# Medical AI Assistant

A **production-ready** Medical Knowledge Assistant RAG pipeline for healthcare professionals to query medical literature, drug interactions, and clinical guidelines. Built with comprehensive safety measures, real-time quality evaluation, and monitoring capabilities.

## 🚀 System Status: **FULLY FUNCTIONAL**

✅ **Core RAG Engine** - Processing medical queries with GPT-4o-mini  
✅ **Safety System** - Multi-layer safety validation with query classification  
✅ **Quality Gates** - RAGAS evaluation with medical-grade thresholds  
✅ **Database Integration** - PostgreSQL with comprehensive logging  
✅ **Monitoring System** - Real-time metrics and health monitoring  
✅ **Docker Deployment** - Production-ready containerization  

## Quick Start

### 1. Environment Setup
```bash
./setup.sh
```

### 2. Configure Environment
Copy and edit the environment file:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Start the System
```bash
# Activate virtual environment
source .venv/bin/activate

# Start API server
OPENAI_API_KEY='your_key_here' python -m uvicorn src.api.main:app --reload --port 8000
```

### 4. Verify System Health
```bash
# Test system components
python test_system_working.py

# Test API health
curl http://localhost:8000/health
```

## 🔧 Testing

For comprehensive testing instructions, see **[TESTING_GUIDE.md](TESTING_GUIDE.md)** which covers:

- Component testing (RAG, Safety, Quality Gates, Database)
- Integration testing with all systems enabled
- API endpoint testing
- Docker deployment testing
- Performance and load testing
- Safety scenario validation
- End-to-end workflow testing

### Quick Test
```bash
# Run comprehensive system verification
python test_system_working.py

# Test specific components
python test_ragas_integration.py
```

## 📡 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `POST /api/v1/query` - Query with RAGAS evaluation and safety validation
- `POST /api/v1/documents/upload` - Upload medical documents
- `GET /api/v1/documents` - List uploaded documents

### Monitoring Endpoints
- `GET /metrics/dashboard` - System metrics dashboard
- `GET /metrics/realtime` - Real-time performance metrics
- `GET /metrics/health` - Detailed health status
- `GET /metrics/evaluation` - RAGAS evaluation metrics

### Example Query with Full Response
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the symptoms of diabetes?"}'
```

**Response includes:**
- Medical answer with source attribution
- RAGAS quality scores (faithfulness, context precision, etc.)
- Quality gate status (pass/fail)
- Safety validation results
- Response time and token usage
- Medical disclaimers

## 🏗️ Architecture

### 5-Layer Production Architecture
1. **API Layer** - FastAPI with comprehensive endpoints
2. **Safety Layer** - Multi-layer safety validation system
3. **RAG Layer** - Document processing and query handling
4. **Evaluation Layer** - RAGAS metrics and quality gates
5. **Data Layer** - PostgreSQL with comprehensive logging

### Project Structure
```
Q1/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # Main API with all endpoints
│   │   └── monitoring_endpoints.py  # Monitoring and metrics
│   ├── core/                  # Core business logic
│   │   ├── embeddings.py      # Custom embedding wrapper
│   │   ├── document_processor.py  # PDF ingestion pipeline
│   │   └── rag_engine.py      # RAG query engine with safety
│   ├── evaluation/            # RAGAS evaluation system
│   │   └── ragas_evaluator.py # Medical RAGAS evaluator
│   ├── safety/               # Safety validation system
│   │   └── safety_system.py  # Multi-layer safety checks
│   ├── database/             # Database models and management
│   │   ├── models.py         # SQLAlchemy models
│   │   └── database.py       # Database connection manager
│   └── __init__.py
├── docker-compose.yml        # Production deployment
├── Dockerfile               # Container configuration
├── nginx.conf              # Reverse proxy configuration
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── TESTING_GUIDE.md       # Comprehensive testing guide
├── .env.example          # Environment template
└── README.md            # This file
```

## 🛡️ Safety Features

### Query Safety Validation
- **Medical Advice Detection**: Blocks diagnosis and treatment requests
- **Harmful Content Filtering**: Prevents dangerous medical misinformation
- **Context Classification**: Categorizes queries for appropriate handling

### Response Safety Measures
- **Quality Gate Enforcement**: Blocks responses below medical-grade thresholds
- **Automatic Disclaimers**: Adds medical disclaimers to all responses
- **Source Attribution**: Always provides source documentation

### Quality Thresholds
- **Faithfulness**: >0.90 (ensures medical accuracy)
- **Context Precision**: >0.85 (ensures relevant information)
- **Real-time Evaluation**: Every response evaluated with RAGAS

## 📊 Monitoring & Metrics

### System Metrics
- Response time tracking (p95 < 3 seconds target)
- Token usage and cost monitoring
- Quality gate pass/fail rates
- Safety blocking statistics

### Health Monitoring
- Database connection health
- Vector store availability
- OpenAI API connectivity
- System resource usage

## 🐳 Docker Deployment

### Development
```bash
# Start with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs medical_ai_api
```

### Production
```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d

# Access through Nginx reverse proxy
curl http://localhost/api/v1/health
```

## 🔬 Technology Stack

### Core Technologies
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Vector DB**: ChromaDB with persistence
- **Framework**: FastAPI + LangChain
- **Database**: PostgreSQL with SQLAlchemy
- **Language**: Python 3.11+

### Evaluation & Safety
- **RAGAS**: Real-time response evaluation
- **Safety System**: Custom medical safety validation
- **Quality Gates**: Medical-grade quality thresholds
- **Monitoring**: Comprehensive metrics collection

### Infrastructure
- **Docker**: Containerized deployment
- **Nginx**: Reverse proxy with security headers
- **Redis**: Caching layer (optional)
- **PostgreSQL**: Production database

## 📈 Performance

### Current Metrics
- **Response Time**: ~7-9 seconds average
- **Token Usage**: ~800-850 tokens per query
- **Sources Retrieved**: 5 relevant documents per query
- **Quality Gate Pass Rate**: Varies by query complexity
- **Safety Blocking**: Effective for medical advice requests

### Optimization Features
- Vector similarity search optimization
- Response caching capabilities
- Batch processing for document ingestion
- Asynchronous API endpoints

## 🚀 Production Readiness

### ✅ Implemented Features
- [x] Core RAG pipeline with medical focus
- [x] RAGAS evaluation system
- [x] Multi-layer safety system
- [x] PostgreSQL database with logging
- [x] Comprehensive monitoring
- [x] Docker containerization
- [x] API documentation (OpenAPI/Swagger)
- [x] Health checks and metrics
- [x] Error handling and logging
- [x] Environment configuration
- [x] Testing framework

### 🔄 Operational Capabilities
- Document upload and processing
- Real-time query handling
- Safety validation and blocking
- Quality assessment and gating
- Performance monitoring
- Health status reporting
- Error tracking and logging

## 🔧 Development & Testing

### Running Tests
```bash
# Comprehensive system test
python test_system_working.py

# RAGAS integration test
python test_ragas_integration.py

# Manual component testing (see TESTING_GUIDE.md)
python test_rag_manual.py
python test_safety_manual.py
python test_quality_gates.py
```

### Adding Documents
```python
# Upload via API
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
     -F "file=@medical_document.pdf"

# Or process directly
python process_pdfs.py
```

### Interactive Querying
```bash
# Start interactive query session
python query_system.py
```

## 🎯 Use Cases

### Healthcare Professionals
- Query medical literature and guidelines
- Research drug interactions and contraindications
- Access clinical decision support information
- Verify medical facts with source attribution

### Medical Students
- Study medical concepts with reliable sources
- Understand complex medical processes
- Access educational medical content
- Learn with built-in safety measures

### Research Applications
- Literature review and analysis
- Medical knowledge extraction
- Clinical guideline interpretation
- Evidence-based information retrieval

## 🛠️ Troubleshooting

### Common Issues
1. **OpenAI API Key**: Ensure proper environment variable setup
2. **Database Connection**: Check PostgreSQL service status
3. **Vector Store**: Verify ChromaDB persistence directory
4. **Dependencies**: Run `pip install -r requirements.txt`

### Debug Commands
```bash
# Check system health
python test_system_working.py

# Verify API server
curl http://localhost:8000/health

# Check database
python -c "from src.database.database import DatabaseManager; print(DatabaseManager().health_check())"
```

## 📚 Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Comprehensive testing instructions
- **[prd.md](prd.md)**: Product Requirements Document
- **API Documentation**: Available at `http://localhost:8000/docs` when running

## 🤝 Contributing

1. Follow the setup steps above
2. Review the testing guide for validation procedures
3. Ensure all tests pass before submitting changes
4. Test with the comprehensive system verification script

## 📄 License

This project is designed for educational and research purposes in medical AI applications.

---

**⚠️ Medical Disclaimer**: This system is designed for educational and research purposes only. It should not be used for actual medical diagnosis or treatment decisions. Always consult qualified healthcare professionals for medical advice. 