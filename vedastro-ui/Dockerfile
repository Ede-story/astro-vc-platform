FROM python:3.9-slim

# Install system dependencies (Classic Swisseph needs compiler)
RUN apt-get update && apt-get install -y \
    wget \
    libgdiplus \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit Settings
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
# Custom Theme
ENV STREAMLIT_THEME_BASE="light"
ENV STREAMLIT_THEME_PRIMARY_COLOR="#666666"
ENV STREAMLIT_THEME_BACKGROUND_COLOR="#FFFFFF"
ENV STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR="#F0F2F6"

CMD ["streamlit", "run", "astro_test_ui.py"]
