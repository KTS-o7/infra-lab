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

# Install aws wrapper so mission commands using --endpoint-url http://localhost:4566
# work transparently inside the container (rewrites to http://floci:4566 internally).
# We replace the venv's aws binary directly so PATH ordering doesn't matter.
COPY aws-wrapper.sh /usr/local/bin/aws-real-install-wrapper
RUN chmod +x /usr/local/bin/aws-real-install-wrapper \
    && mv /app/.venv/bin/aws /app/.venv/bin/aws-real \
    && cp /usr/local/bin/aws-real-install-wrapper /app/.venv/bin/aws \
    && chmod +x /app/.venv/bin/aws

COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
