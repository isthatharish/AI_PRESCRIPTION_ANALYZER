# 🏥 AI Prescription Analyzer

> **AI-powered healthcare platform that acts as a guardian for medical prescriptions**

An advanced healthcare platform that leverages AI to extract prescription details from text/images, detect dangerous drug interactions, recommend safe alternatives, and provide personalized medication management with HIPAA/GDPR compliance.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red)

## 🌟 Key Features

### 🔍 **OCR & NLP Extraction**
- Extract drug names, dosage, and frequency from both digital and handwritten prescriptions
- Support for JPG, PNG, and PDF files
- Advanced image preprocessing for better OCR accuracy
- Dual OCR engines (Tesseract + EasyOCR) for maximum reliability

### ⚠️ **Drug Interaction Detection**
- Real-time analysis of dangerous drug combinations
- Age-specific dosage validation
- Comprehensive drug database with FDA-approved medications
- Risk severity classification (Severe, Moderate, Minor)

### 💊 **Smart Medication Management**
- Alternative medication suggestions when risks are detected
- Personalized dosage recommendations based on age and medical history
- Medication timeline tracking and adherence monitoring

### 🔐 **Secure Membership System**
- JWT-based authentication with role-based access control
- HIPAA/GDPR compliant data encryption
- Secure health records and prescription history
- Multi-role dashboards (Patient, Doctor, Pharmacist)

### 🗺️ **Pharmacy Integration**
- Interactive pharmacy mapping with Google Maps
- Real-time medication availability checking
- Distance-based pharmacy recommendations
- Direct contact and directions integration

### 📱 **Smart Notifications**
- Medication reminders and refill alerts
- Drug interaction warnings
- Doctor appointment follow-ups
- SMS and email notification support

### 🤖 **AI Health Assistant**
- Powered by IBM Granite (granite-3.3-2b-base) and Hugging Face models
- Medical query processing and medication advice
- Side effects information and dosage guidance
- 24/7 availability for health-related questions

## 🛠️ Technology Stack

### **Backend**
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Core programming language
- **PostgreSQL** - Primary database for secure data storage
- **Redis** - Caching and session management
- **SQLAlchemy** - Database ORM and migrations

### **Frontend**
- **Streamlit** - Interactive web application framework
- **React/Next.js** - Production-ready frontend (planned)
- **Plotly** - Data visualization and charts
- **Bootstrap** - Responsive UI components

### **AI/ML Models**
- **IBM Granite** - granite-3.3-2b-base for medical reasoning
- **Hugging Face Transformers** - NLP processing and entity extraction
- **Tesseract OCR** - Text extraction from images
- **EasyOCR** - Alternative OCR engine for better accuracy
- **OpenCV** - Image preprocessing and computer vision

### **Integrations**
- **Google Maps API** - Pharmacy location services
- **Twilio** - SMS notifications and alerts
- **Firebase** - Push notifications and real-time updates
- **FDA API** - Drug database and interaction data

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+
- Redis Server
- Git
- Google Maps API key
- Hugging Face API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-prescription-analyzer.git
cd ai-prescription-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your configuration
nano .env
```

**Required Environment Variables:**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/prescription_analyzer
HUGGINGFACE_API_KEY=hf_your_hugging_face_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
SECRET_KEY=your-super-secret-jwt-key-change-this
```

### 3. Database Setup

```bash
# Create database
createdb prescription_analyzer

# Run migrations
alembic upgrade head
```

### 4. Start the Application

**Backend API:**
```bash
cd backend
python main.py
```
API will be available at: http://localhost:8000

**Frontend (Streamlit):**
```bash
cd frontend/streamlit_app
streamlit run main.py
```
Frontend will be available at: http://localhost:8501

## 📖 Usage Guide

### 1. **Account Registration**
1. Open the Streamlit frontend
2. Click "Register" tab
3. Fill in your details (email, password, full name, age)
4. Select your role (Patient, Doctor, Pharmacist)
5. Complete registration and login

### 2. **Upload Prescription**
1. Navigate to "Upload Prescription"
2. Choose between image upload or manual entry
3. Upload a clear photo of your prescription
4. AI will process and extract medication details
5. Review and confirm the extracted information

### 3. **Drug Interaction Checking**
1. Go to "Drug Interactions" page
2. View your current medications
3. Add new medications to check for interactions
4. Review detailed interaction analysis and recommendations

### 4. **AI Health Assistant**
1. Access the "AI Chatbot" page
2. Ask questions about medications, side effects, dosages
3. Use quick question buttons for common queries
4. Get 24/7 AI-powered health guidance

### 5. **Find Nearby Pharmacies**
1. Visit "Pharmacy Finder"
2. Enter your location or use GPS
3. Set search radius
4. View nearby pharmacies with medication availability
5. Get directions and contact information

## 🏗️ Project Structure

```
ai-prescription-analyzer/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application entry
│   ├── routers/               # API route handlers
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   ├── middleware/            # Security & logging
│   └── utils/                 # Helper functions
├── frontend/
│   ├── streamlit_app/         # Streamlit frontend
│   └── react_app/             # React frontend (future)
├── ai_models/                 # AI/ML modules
│   ├── ocr/                   # OCR processing
│   ├── nlp/                   # Natural language processing
│   └── chatbot/               # AI assistant
├── database/                  # Database schemas & migrations
├── tests/                     # Unit and integration tests
├── docs/                      # Documentation
├── scripts/                   # Deployment & utility scripts
├── config/                    # Configuration files
└── data/                      # Sample data & datasets
```

## 🔧 API Documentation

The FastAPI backend provides a comprehensive REST API. When running in debug mode, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key API Endpoints

```
POST /api/v1/auth/register     # User registration
POST /api/v1/auth/login        # User authentication
GET  /api/v1/prescriptions     # List user prescriptions
POST /api/v1/prescriptions/upload  # Upload prescription image
POST /api/v1/interactions/check    # Check drug interactions
POST /api/v1/chatbot/chat      # AI assistant chat
GET  /api/v1/pharmacy/nearby   # Find nearby pharmacies
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_prescriptions.py
```

## 🔒 Security & Compliance

### HIPAA Compliance
- End-to-end encryption for all patient data
- Audit logging for all access and modifications
- Secure authentication with JWT tokens
- Role-based access control (RBAC)
- Data anonymization for analytics

### GDPR Compliance
- Explicit user consent for data processing
- Right to data portability and deletion
- Privacy by design architecture
- Data minimization principles
- Transparent privacy policies

### Security Features
- TLS/SSL encryption for all communications
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting and DDoS protection
- Security headers middleware

## 📊 Monitoring & Analytics

- **Application Metrics**: FastAPI built-in metrics
- **Health Checks**: `/api/v1/health` endpoint
- **Error Tracking**: Sentry integration
- **Logging**: Structured logging with Loguru
- **Performance**: Redis caching for optimization

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

```bash
# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start Streamlit
streamlit run frontend/streamlit_app/main.py --server.port 8501
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@prescription-analyzer.com
- 💬 Discussions: GitHub Discussions
- 🐛 Bug Reports: GitHub Issues
- 📖 Documentation: [docs.prescription-analyzer.com](docs.prescription-analyzer.com)

## 🙏 Acknowledgments

- **IBM Granite** - Advanced AI reasoning capabilities
- **Hugging Face** - NLP models and transformers
- **FDA** - Drug interaction and safety data
- **OpenStreetMap** - Pharmacy location data
- **Tesseract** - Open-source OCR engine

## 🗺️ Roadmap

### Version 2.0 (Q2 2024)
- [ ] React/Next.js production frontend
- [ ] Mobile app (React Native)
- [ ] Advanced drug interaction algorithms
- [ ] Pharmacy inventory integration
- [ ] Telemedicine integration

### Version 3.0 (Q4 2024)
- [ ] Multi-language support
- [ ] Blockchain prescription tracking
- [ ] Predictive health analytics
- [ ] IoT device integration
- [ ] Advanced AI reasoning with GPT-4

---

**Built with ❤️ for better healthcare outcomes**

*For more information, visit our [website](https://prescription-analyzer.com) or contact our [support team](mailto:support@prescription-analyzer.com).*