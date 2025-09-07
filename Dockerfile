# Stage 1: Builder
FROM python:3.12-slim AS builder

# Install uv
RUN pip install uv ruff

# Set up virtual environment
WORKDIR /app
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files and install dependencies
COPY pyproject.toml ./
RUN uv pip install --no-cache .

# Stage 2: Final image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv ./.venv

# Copy application code
COPY src/ ./src/

# Set path to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
