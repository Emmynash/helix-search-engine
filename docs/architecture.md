 # System Architecture — Helix Search Engine

 ## High-Level Design Pattern

 We use a CQRS (Command Query Responsibility Segregation) pattern to separate the read-heavy search path from the write-intensive crawl path. This prevents large crawl workloads (≈4B pages/month) from impacting search latency (≈100B queries/month).

 ## Core Components & Scalability

 ### Ingestion Layer (Write Path)

 The write path is optimized for throughput, durability, and resilience.

 #### Crawl API Service
 - **Role:** Accepts crawl requests, validates permissions/quotas, and enqueues jobs.
 - **Implementation:** Stateless Python service (e.g., `FastAPI`).
 - **Scaling:** Horizontal autoscaling of containers based on CPU/memory and queue depth.

 #### Message Bus (`Kafka` / `RabbitMQ`)
 - **Role:** Buffers ingestion bursts and decouples producers from workers.
 - **Priority Topics:**
	 - ``topic-crawl-high-priority`` — on-demand user crawls (SLA: 1 hour).
	 - ``topic-crawl-background`` — bulk churn (regular crawling).

 #### Worker Nodes (Crawler)
 - **Role:** Consume crawl messages, fetch pages, parse DOM, extract text, and compute document signatures.
 - **Scaling:** Scale based on consumer lag; e.g., if `high-priority` depth > 1000, spin up additional pods.

 ### Storage Layer

 We apply a polyglot persistence strategy to balance cost and performance.

 - **Blob Store (`S3` / `GCS`)**: Stores raw compressed HTML/PDF blobs (cheap cold storage).
 - **Metadata Store (`Postgres` / `Cassandra`)**: Stores URL frontier, job statuses, and user metadata. Shard by `url_hash` to distribute write load.
 - **Inverted Index (`Elasticsearch` / `OpenSearch`)**: Stores token → document postings.
	 - Sharding: 50+ shards to distribute index size.
	 - Replication: 3+ replicas per shard to handle high read QPS (≈38k QPS).

 ### Query Layer (Read Path)

 The read path is engineered for low latency and high availability.

 - **Search API Service** — parses queries, applies ranking/function scoring, and formats responses.
 - **Global CDN & WAF (`Cloudflare` / `CloudFront`)** — caches static assets and mitigates DDoS.
 - **Application Cache (`Redis` Cluster)** — caches popular query result sets (top ~10% queries), reducing load on the index by ~60–80% (Zipf distribution).

 ## Data Flow Summaries

 ### Flow 1 — Search Request
 1. Client: `GET /search?q=python`
 2. Load balancer / API edge checks `Redis` cache — if hit, return cached results.
 3. On cache miss, `Search API` constructs the ES query (boolean + function scoring).
 4. `Elasticsearch` performs scatter-gather across shards and returns candidate hits.
 5. Results are ranked, cached in `Redis` (TTL: 5m), and returned to the client.

 ### Flow 2 — On-Demand Crawl (SLA)
 1. Client: `POST /crawl` with `priority=high`.
 2. `Crawl API` enqueues message to ``topic-crawl-high-priority``.
 3. Worker consumes message, fetches the URL, parses and extracts text.
 4. Artifacts saved:
		- Raw HTML → `S3`
		- Metadata / job status → `Postgres` (or `Cassandra` for scale)
		- Document tokens → `Elasticsearch`
 5. Job status updated to `complete` in `Redis` / `Postgres`.

 ## Notes & SLAs
 - Use priority queues to satisfy on-demand SLAs while keeping background crawling throughput high.
 - Autoscaling triggers should be based on measurable signals (consumer lag, queue depth, CPU, memory).
 - Cache the hottest queries and tune TTLs based on observed hit ratios.

 ## Appendix (Key Endpoints)
 - `GET /search?q=<query>` — search endpoint
 - `POST /crawl` (body: `{ "url": "...", "priority": "high|normal" }`) — request a crawl
