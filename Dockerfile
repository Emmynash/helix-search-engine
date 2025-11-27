# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Security: Create non-root user
RUN groupadd -r atlas && useradd -r -g atlas atlas

# Copy dependencies from builder
COPY --from=builder /root/.local /home/atlas/.local
COPY ./app ./app

# Set environment
ENV PATH=/home/atlas/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER atlas

# Run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]