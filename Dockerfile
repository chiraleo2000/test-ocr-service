# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=th_TH.UTF-8
ENV LANGUAGE=th_TH:th
ENV LC_ALL=th_TH.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    locales \
    poppler-utils \
    libpoppler-cpp-dev \
    tesseract-ocr \
    tesseract-ocr-tha \
    libmagic1 \
    fonts-thai-tlwg \
    ghostscript \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Thai Language Support
RUN apt-get install language-pack-th

# Configure locales for Thai language support
RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen th_TH.UTF-8 && \
    update-locale LANG=th_TH.UTF-8

# Install Python dependencies including pdf2image
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir pdf2image

# Set working directory
WORKDIR /app

# Copy only necessary files to /app
COPY app.py /app/
COPY .env /app/

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
