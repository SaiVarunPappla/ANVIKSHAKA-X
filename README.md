# ANVIKSHAKA-X

**AI-Powered Naval Mission Planning & Risk Assessment System**

A command-and-control platform that combines multiple AI agents, machine learning, and a tactical interface to automate naval mission planning, risk assessment, resource optimization, and predictive maintenance.

## Overview

ANVIKSHAKA-X automates naval mission planning through a multi-agent AI system. Five specialized agents work sequentially to analyze missions, assess risks, optimize resource allocation, and predict equipment failures.

### Core Features

- **Multi-Agent AI Pipeline** — Five agents collaborate to provide comprehensive mission analysis
- **Risk Assessment** — Evaluates threats based on weather, duration, and operational factors
- **Predictive Maintenance** — Machine learning-powered failure probability predictions
- **Natural Language Interface** — Parse plain English commands into structured missions
- **Glassmorphism UI** — Modern interface with smooth animations and responsive design
- **Local AI Integration** — Optional Ollama/LLaMA3 support for enhanced narratives

## Architecture

### System Overview

```mermaid
graph TB
    subgraph Frontend["React Frontend (Port 5173)"]
        UI[Tactical Dashboard]
        Router[React Router]
        Pages[6 Main Pages]
    end
    
    subgraph Backend["FastAPI Backend (Port 8000)"]
        API[REST API]
        Agents[5 AI Agents]
        DB[(SQLite Database)]
        ML[ML Model]
    end
    
    subgraph External["Optional AI"]
        Ollama[Ollama LLM]
    end
    
    UI -->|HTTP/Axios| API
    API --> Agents
    Agents --> DB
    Agents -.->|Optional| Ollama
    Agents --> ML
    ML --> DB
```

### AI Agent Pipeline

Five specialized agents execute sequentially to analyze each mission:

```mermaid
graph LR
    A[Mission Request] --> B[1. Mission Planner]
    B --> C[2. Risk Analyst]
    C --> D[3. Resource Optimizer]
    D --> E[4. Maintenance Analyst]
    E --> F[5. Supervisor]
    F --> G[Consolidated Brief]
    
    B -.->|Optional| AI[Ollama LLM]
    C -.->|Optional| AI
    E -.->|Optional| AI
    F -.->|Optional| AI
    
    E --> ML[(ML Model)]
```

#### Agent Responsibilities

| Agent | Purpose | Output |
|-------|---------|--------|
| **Mission Planner** | Plans route, strategy, timeline, asset roles | Waypoints, tactical approach, phase timeline |
| **Risk Analyst** | Evaluates threats, weather, duration impact | Risk score (0-100), success probability, high-risk zones |
| **Resource Optimizer** | Allocates assets by battery health & capability | Primary/backup roles, coverage percentage |
| **Maintenance Analyst** | Predicts failures using ML model | Failure probability per asset, risk classification |
| **Supervisor** | Consolidates all outputs into command brief | Final mission brief, contingency plans, alerts |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (optional, for AI-enhanced narratives)

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/SaiVarunPappla/ANVIKSHAKA-X.git
cd ANVIKSHAKA-X
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train ML model (first time only)
cd ../ml
python generate_dataset.py
python train_model.py
cd ../backend

# Start backend server
python main.py
```

Backend will run on `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

#### 4. Optional: Ollama Setup

For AI-enhanced narratives, install Ollama and pull the LLaMA3 model:

```bash
# Install Ollama from https://ollama.ai

# Pull llama3 model
ollama pull llama3

# Verify
ollama list
```

The system automatically detects Ollama and uses it when available. Without Ollama, the system falls back to rule-based logic.

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Development database (PostgreSQL ready) |
| **Pydantic** | Data validation and settings management |
| **scikit-learn** | ML model training (Random Forest) |
| **pandas/numpy** | Data processing and analysis |
| **Ollama** | Local LLM integration (optional) |
| **httpx** | Async HTTP client |
| **joblib** | Model persistence |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | Modern UI library with hooks |
| **Vite** | Build tool |
| **React Router v6** | Client-side routing |
| **Tailwind CSS** | Utility-first CSS framework |
| **Framer Motion** | Animations and transitions |
| **Recharts** | Data visualization charts |
| **Axios** | HTTP client for API calls |
| **Lucide React** | Icon library |

### DevOps
| Tool | Purpose |
|------|---------|
| **uvicorn** | ASGI server for FastAPI |
| **PostCSS** | CSS processing |
| **Autoprefixer** | CSS vendor prefixing |

## Repository Structure

```
anvikshaka-x/
├── backend/                    # FastAPI backend server
│   ├── agents/                 # AI agent implementations
│   │   ├── base_agent.py      # Base class with Ollama integration
│   │   ├── mission_planner.py  # Agent 1: Route & strategy planning
│   │   ├── risk_analyst.py     # Agent 2: Risk assessment
│   │   ├── resource_optimizer.py # Agent 3: Asset allocation
│   │   ├── maintenance_analyst.py # Agent 4: ML predictions
│   │   ├── supervisor.py       # Agent 5: Consolidation
│   │   └── nlp_commander.py    # Natural language parser
│   ├── routers/                # API route handlers
│   │   ├── mission.py          # Mission CRUD + agent pipeline
│   │   ├── risk.py             # Risk analysis endpoints
│   │   ├── maintenance.py      # Maintenance predictions
│   │   ├── dashboard.py        # Dashboard aggregations
│   │   ├── chat.py             # AI chat interface
│   │   └── commander.py        # NLP command parsing
│   ├── main.py                 # FastAPI application entry
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # ORM models (5 tables)
│   ├── schemas.py              # Pydantic request/response schemas
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── pages/              # Main application pages
│   │   │   ├── Dashboard.jsx   # KPI overview & recent missions
│   │   │   ├── MissionPlanner.jsx # Mission creation form
│   │   │   ├── RiskDashboard.jsx # Risk analysis results
│   │   │   ├── Maintenance.jsx  # Predictive maintenance
│   │   │   ├── Analytics.jsx    # Fleet analytics charts
│   │   │   └── Chat.jsx         # AI chat interface
│   │   ├── components/         # Reusable components
│   │   │   ├── Sidebar.jsx     # Navigation sidebar
│   │   │   ├── Navbar.jsx      # Page header
│   │   │   ├── KPICard.jsx     # Metric display cards
│   │   │   ├── MissionForm.jsx # Mission input form
│   │   │   ├── RiskPanel.jsx   # Risk visualization
│   │   │   ├── MaintenanceTable.jsx # Prediction table
│   │   │   └── AgentOutputPanel.jsx # Agent results display
│   │   ├── lib/
│   │   │   └── api.js          # Axios API client
│   │   ├── App.jsx             # Root component with routing
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global styles + Tailwind
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   └── tailwind.config.js      # Tailwind customization
│
├── ml/                         # Machine Learning module
│   ├── data/
│   │   └── synthetic_assets.csv # Training dataset
│   ├── models/
│   │   └── maintenance_model.pkl # Trained Random Forest
│   ├── generate_dataset.py     # Synthetic data generator
│   ├── train_model.py          # Model training script
│   └── predict.py              # Prediction interface
│
└── docs/                       # Documentation
    ├── archive/                # Historical development notes
    └── internal/               # Technical documentation
```

## System Workflow

### Mission Lifecycle

```mermaid
stateDiagram-v2
    [*] --> MissionCreation
    
    MissionCreation --> FormInput: User fills form
    MissionCreation --> NLPCommand: Natural language
    
    FormInput --> AgentPipeline: POST /api/mission
    NLPCommand --> AgentPipeline: POST /api/commander
    
    AgentPipeline --> MissionPlanner: Agent 1
    MissionPlanner --> RiskAnalyst: Agent 2
    RiskAnalyst --> ResourceOptimizer: Agent 3
    ResourceOptimizer --> MaintenanceAnalyst: Agent 4
    MaintenanceAnalyst --> Supervisor: Agent 5
    
    Supervisor --> DatabasePersist: Save results
    DatabasePersist --> DisplayResults: Return to frontend
    
    DisplayResults --> [*]: Mission complete
```

### Data Flow

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as Backend
    participant DB as Database
    participant Agent as AI Agents
    participant LLM as Ollama
    participant ML as ML Model
    
    UI->>API: POST /api/mission
    API->>DB: INSERT Mission
    DB-->>API: mission_id
    
    API->>Agent: Run 5-agent pipeline
    Agent->>LLM: Request AI narrative (optional)
    LLM-->>Agent: Enhanced text
    Agent->>ML: Predict asset failures
    ML-->>Agent: Failure probabilities
    Agent-->>API: Consolidated results
    
    API->>DB: INSERT RiskAssessment, AgentLogs
    API-->>UI: Mission brief + agent outputs
    UI->>UI: Display with animations
```

## Frontend Details

The frontend uses React 18 with Vite, featuring a glassmorphism design system built with Tailwind CSS and Framer Motion animations.

### Key Pages

| Page | Purpose |
|------|---------|
| **Dashboard** | Live KPIs, recent missions, system status |
| **Mission Planner** | Form-based mission creation with asset allocation |
| **Risk Dashboard** | Risk analysis with score cards and zone visualization |
| **Maintenance** | ML-powered failure predictions with risk classification |
| **Analytics** | Fleet health charts and mission success metrics |
| **Chat** | Natural language interface for mission commands |

## API Endpoints

#### Mission Management
```http
POST   /api/mission              # Create mission + run all agents
GET    /api/missions             # List all missions
GET    /api/agent-logs/{id}      # Get agent logs for mission
POST   /api/commander            # Natural language mission creation
```

#### Analysis & Predictions
```http
POST   /api/risk-analysis        # Analyze risk for specific mission
POST   /api/maintenance          # Run ML predictions for assets
GET    /api/assets               # List all assets
```

#### Dashboard & Monitoring
```http
GET    /api/dashboard            # Aggregated KPIs and stats
POST   /api/chat                 # Chat with AI assistant
GET    /api/health               # System health check
```

### Database Schema

```sql
-- Mission: stores every mission submitted
missions (
    id, name, mission_type, duration_hours,
    threat_level, weather, num_drones, num_auvs,
    num_torpedoes, num_launchers, status, created_at
)

-- Asset: drones, AUVs, torpedoes, launchers
assets (
    id, name, asset_type, battery_health,
    operating_hours, mission_count, status, last_maintenance
)

-- RiskAssessment: risk analysis results per mission
risk_assessments (
    id, mission_id, risk_score, risk_category,
    success_probability, high_risk_zones,
    route_suggestion, agent_output_json, created_at
)

-- MaintenancePrediction: ML predictions per asset
maintenance_predictions (
    id, asset_id, failure_probability, risk_level,
    recommended_action, predicted_at
)

-- AgentLog: audit trail of agent invocations
agent_logs (
    id, mission_id, agent_name, input_summary,
    output_json, created_at
)
```

### Machine Learning

The system uses a Random Forest Classifier trained on 7 features to predict asset failure probability:

```python
# Features used for prediction
features = [
    "battery_health",      # 0-100 percentage
    "operating_hours",     # Total hours in operation
    "mission_count",       # Number of missions completed
    "temperature",         # Operating temperature (°C)
    "humidity",            # Environmental humidity (%)
    "vibration_level",     # Vibration sensor reading
    "pressure"             # Atmospheric pressure (atm)
]

# Output: Failure probability (0.0 - 1.0)
# Risk classification: low / medium / high / critical
```

Training details:
- 1000 synthetic asset samples
- 80/20 train-test split
- Persisted with joblib
- Graceful fallback to heuristics if model unavailable

## Configuration

Environment variables for backend (create `.env` in `backend/` directory):

```bash
# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./anvikshaka.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Ollama (optional)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Logging
LOG_LEVEL=INFO
```

Frontend environment (create `.env` in `frontend/` directory):

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000/api
```

## Deployment

### Backend

Docker deployment example:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY ml/ ../ml/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Production recommendations:
- Switch to PostgreSQL from SQLite
- Configure CORS for production domain
- Set up logging
- Deploy Ollama separately if using AI features

### Frontend

```bash
cd frontend
npm run build
# Outputs to frontend/dist/
```

Deploy to Vercel, Netlify, AWS S3 + CloudFront, or Nginx.

Configure production API URL:
```bash
VITE_API_URL=https://your-api-domain.com/api
```

## Known Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| **Dashboard connection beams** misaligned on mobile | Cosmetic | Beams work correctly on desktop (1024px+) |
| **SQLite concurrent writes** limited | Development only | Use PostgreSQL in production |
| **Ollama cold start** 5-10 seconds | First LLM call | Warm-up on server startup |
| **ML model requires training** | First-time setup | Run training scripts once |
| **No real-time updates** | Manual refresh needed | Future WebSocket implementation |

## Future Improvements

Planned features:

- Real-time mission tracking via WebSockets
- Multi-user collaboration with role-based access
- Mission replay and simulation mode
- Enhanced ML models for better predictions
- Export mission briefs to PDF/JSON
- Map integration for route visualization
- Historical trend analysis
- Mobile-responsive optimizations
- Offline mode with service workers
- Custom agent configurations

Technical priorities:

- Migrate to PostgreSQL
- Add test coverage (unit + integration)
- Implement authentication/authorization
- Add API rate limiting
- Set up CI/CD pipeline
- Add Swagger/OpenAPI documentation
- Implement caching with Redis

## Contributing

Contributions are welcome. Please follow these guidelines:

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following existing code style
4. Test your changes across backend, frontend, and ML components
5. Commit with clear messages: `git commit -m "feat: add new feature"`
6. Push and create a Pull Request

### Code Style

**Python (Backend):**
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to classes and functions
- Keep functions focused and single-purpose

**JavaScript (Frontend):**
- Use functional components with hooks
- Follow React best practices
- Use destructuring for props
- Keep components under 200 lines when possible

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the async web framework
- React Team for the UI library
- Ollama for making local LLMs accessible
- scikit-learn for ML tools
- Tailwind CSS for the utility-first framework
- Framer Motion for animation capabilities

## Contact

- Issues: [GitHub Issues](https://github.com/SaiVarunPappla/ANVIKSHAKA-X/issues)
- Discussions: [GitHub Discussions](https://github.com/SaiVarunPappla/ANVIKSHAKA-X/discussions)
