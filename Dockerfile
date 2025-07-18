FROM python:3.12-slim

WORKDIR /app
# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt



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
