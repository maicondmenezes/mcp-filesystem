# Stage 1: Build stage
FROM python:3.8-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only dependency files to leverage Docker cache
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Final stage
FROM python:3.8-slim

WORKDIR /app

# Copy virtual env from builder stage
COPY --from=builder /app/.venv /.venv

# Activate virtual env
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY mcp_filesystem ./mcp_filesystem

# Set the entrypoint
ENTRYPOINT ["mcp-filesystem"]
CMD ["start"]
