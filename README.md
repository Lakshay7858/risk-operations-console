# Trade Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Interactive analytics dashboard for customs trade data. Built with a **FastAPI** backend and **React** frontend, the platform delivers real-time charts, risk heatmaps, and drill-down analysis for trade compliance teams. Designed to surface anomalies in import/export declarations, highlight high-risk corridors, and provide actionable intelligence on trade patterns.

## Screenshots

> **Dashboard Overview** -- Main view showing trade volume trends (line chart), risk distribution heatmap by country and HS chapter, and KPI summary cards for total declarations, flagged shipments, and average risk score.

![Dashboard Overview](docs/screenshots/dashboard-overview.png)

> **Trade Volume Trends** -- Time-series line chart with selectable granularity (daily, weekly, monthly). Supports overlay of multiple commodity groups and export to CSV.

![Trade Volume](docs/screenshots/trade-volume.png)

> **Risk Heatmap** -- Color-coded matrix of risk scores across origin countries and HS code chapters. Click any cell to drill down into individual declarations.

![Risk Heatmap](docs/screenshots/risk-heatmap.png)

> **Top Importers/Exporters** -- Ranked table of traders by volume and value, with risk score badges and trend sparklines. Filterable by date range and commodity.

![Top Traders](docs/screenshots/top-traders.png)

> **Anomaly Timeline** -- Chronological view of detected anomalies with severity indicators, linked declarations, and rule-match details.

![Anomaly Timeline](docs/screenshots/anomaly-timeline.png)

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | FastAPI, SQLAlchemy, asyncpg        |
| Frontend    | React 18, React Router, Chart.js    |
| Database    | PostgreSQL 15                       |
| Cache       | Redis 7                             |
| Auth        | JWT (python-jose)                   |
| Containers  | Docker, Docker Compose              |

## Features

- **Trade Volume Trends** -- Interactive line charts with configurable time windows and commodity filters
- **Risk Distribution Heatmap** -- Country-by-HS-chapter risk matrix with drill-down capability
- **Top Importers/Exporters** -- Ranked tables with volume, value, and composite risk scores
- **HS Code Analysis** -- Breakdown of trade activity by harmonized system classification
- **Anomaly Timeline** -- Chronological detection feed with severity scoring and declaration links
- **Real-time Filtering** -- Cross-dashboard filters for date range, country, HS code, and risk threshold
- **REST API** -- Fully documented OpenAPI endpoints for programmatic access

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 3000, 8000, 5432, and 6379 available

### Run with Docker

```bash
git clone https://github.com/ShahinHasanov90/trade-analytics-dashboard.git
cd trade-analytics-dashboard
docker-compose up --build
```

The services will be available at:

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| Backend   | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |
| PostgreSQL| localhost:5432               |
| Redis     | localhost:6379               |

### Development Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

### Environment Variables

| Variable            | Default                                      | Description            |
|---------------------|----------------------------------------------|------------------------|
| `DATABASE_URL`      | `postgresql+asyncpg://trade:trade@db:5432/tradedb` | PostgreSQL connection  |
| `REDIS_URL`         | `redis://redis:6379/0`                       | Redis connection       |
| `SECRET_KEY`        | `change-me-in-production`                    | JWT signing key        |
| `CORS_ORIGINS`      | `http://localhost:3000`                      | Allowed CORS origins   |

## Project Structure

```
trade-analytics-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   ├── config.py      # Application settings
│   │   └── main.py        # FastAPI application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── App.jsx        # Root component with routing
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Method | Endpoint                        | Description                        |
|--------|---------------------------------|------------------------------------|
| GET    | `/api/v1/trades`                | List trade declarations (paginated)|
| GET    | `/api/v1/trades/{id}`           | Get single declaration             |
| GET    | `/api/v1/trades/search`         | Filter declarations                |
| GET    | `/api/v1/analytics/volume`      | Trade volume time series           |
| GET    | `/api/v1/analytics/top-traders` | Top importers/exporters            |
| GET    | `/api/v1/analytics/hs-breakdown`| HS code distribution               |
| GET    | `/api/v1/analytics/anomalies`   | Detected anomalies                 |
| GET    | `/api/v1/risk/heatmap`          | Risk score heatmap data            |
| GET    | `/api/v1/risk/scores`           | Risk scores (paginated)            |
| GET    | `/api/v1/risk/distribution`     | Risk score distribution            |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
