FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies needed by some Python packages (Pillow, PyMuPDF, OpenCV-ish libs)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       wget \
       libgl1 \
       libglib2.0-0 \
       libsm6 \
       libxrender1 \
       libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source
COPY . /app

# Port used by Streamlit
ENV PORT=8080
EXPOSE 8080

# Start Streamlit
CMD ["sh", "-c", "streamlit run main.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"]
