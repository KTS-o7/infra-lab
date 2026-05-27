FROM python:3.14.5-slim

WORKDIR /app

# Install system dependencies
# zip is required for Lambda function packaging in mission commands
# awscli installed via pip so it works on both amd64 and arm64 (no standalone binary)
RUN apt-get update && apt-get install -y \
    zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen

COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
