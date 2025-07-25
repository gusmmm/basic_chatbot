FROM python:3.12-slim

WORKDIR /app
# Copy application files

RUN pip install uv

COPY pyproject.toml ./

# ✅ BEST: Use a cache mount to persist the uv cache directory
# The target path `/root/.cache/uv` is the default cache location for uv.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

COPY . .
# Expose the port that Streamlit runs on
EXPOSE 8501

# Configure Streamlit to run in headless mode
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false

# Run Streamlit with proper configuration for Docker
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
