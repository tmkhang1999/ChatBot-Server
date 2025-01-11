FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf8

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    git \
    pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "app.py"]