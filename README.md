# Helix Search Engine

## System Architecture & Scale Strategy

### The Scale Problem
We are designing for:
- **Write Heavy Load:** 4B pages/month (~1,500/sec).
- **Read Extreme Load:** 100B queries/month (~38k/sec avg, ~150k/sec peak).

### Architectural Decisions

1.  **CQRS (Command Query Responsibility Segregation):**
    The read API (Search) and the write API (Crawl) will be completely decoupled.
    - **Writes:** Go to a Kafka/RabbitMQ priority queue (to handle the 1-hour SLA vs general background crawls).
    - **Reads:** Hit a Redis Cache first, then the Search Index (Elasticsearch/OpenSearch).

2.  **Asynchronous Crawling:**
    The `POST /crawl` endpoint will not crawl the page. It will acknowledge the request and push it to a queue. This prevents thread starvation on the API server.

3.  **Database Strategy:**
    - **Metadata Store (Postgres):** User accounts, API keys, Job statuses.
    - **Blob Store (S3/GCS):** Raw HTML content.
    - **Inverted Index (Elasticsearch):** Searchable tokens.