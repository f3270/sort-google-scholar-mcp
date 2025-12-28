# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables to ensure Python doesn't buffer outputs
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src ./src

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Set the entry point to use sortgs via uv
ENTRYPOINT ["uv", "run", "sortgs"]

# By default, run sortgs with an example search keyword
CMD ["--help"]
