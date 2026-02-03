FROM python:3.13.11-slim

WORKDIR /app

# Install dependencies
COPY scripts/requirements.txt scripts/
RUN pip install --no-cache-dir -r scripts/requirements.txt

# Copy scripts and schemas
COPY scripts/ scripts/
COPY schemas/ schemas/

# Data is mounted at runtime
VOLUME /app/data

ENTRYPOINT ["python"]
