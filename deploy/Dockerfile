FROM python:3.12-slim-bookworm

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy deployment artifacts
COPY requirements.txt /app/deploy/
COPY *.whl /app/deploy/
COPY alembic /app/deploy/alembic
COPY alembic.ini /app/deploy/

# Install dependencies
RUN pip install -r /app/deploy/requirements.txt

# Install the application wheel package
RUN pip install /app/deploy/*.whl
