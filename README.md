# Helix Search Engine

Helix Search Engine 🌍 is a scalable, distributed search backend designed to handle billions of crawls and queries. The project focuses on high-throughput ingestion, low-latency search, and operational resilience.

## Overview

- **Architecture pattern:** CQRS (Command Query Responsibility Segregation) to decouple ingestion (crawling) from retrieval (searching).
- **Docs:**
	- `docs/architecture.md` — System architecture and data flow.
	- `docs/api-spec.md` — API endpoints and examples.

## Key Scalability Decisions

- **Async ingestion:** Writes are buffered via Kafka priority queues to enforce on-demand SLAs while processing large background crawl volumes.
- **Tiered storage:**
	- Hot: `Redis` cluster for most-frequent queries.
	- Warm: `Elasticsearch` (inverted index) for general search.
	- Cold: `S3` for raw HTML/PDF blobs.
- **Horizontal scaling:** Stateless Python workers autoscale based on queue lag (consumer offset) and resource utilization.

## Getting Started

### Prerequisites

- `Python 3.11+`
- `Docker` & `Docker Compose`
- `Redis` & `PostgreSQL` (or use the provided `docker-compose`)

### Installation

1. Clone the repository:

```powershell
git clone https://github.com/emmynash/helix-search-engine.git
cd helix-search-engine
```

2. (Optional) Create and activate a virtual environment:

```powershell
python -m venv .venv; ./.venv/Scripts/Activate.ps1
```

3. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

4. Start the development environment (Redis, Postgres, mock services):

```powershell
docker-compose up -d
```

## Development

- Run tests: `pytest` (if tests are present).
- Linting: `ruff` / `black` (if configured in the repo).

## Contributing

Please open issues or pull requests against the `main` branch. Follow the code style and run tests before submitting changes.

## License

See `LICENSE` (if present) for license details.

