FROM python:3.12-slim-bookworm

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/deploy/
RUN pip install -r /app/deploy/requirements.txt

# Copy deployment artifacts
COPY *.whl /app/deploy/
COPY alembic /app/deploy/alembic
COPY alembic.ini /app/deploy/

# Install the application wheel package
RUN pip install /app/deploy/*.whl
