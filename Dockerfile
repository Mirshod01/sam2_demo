# Multi-stage build for SAM2 Demo
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY demo/frontend/package*.json ./
RUN npm install
COPY demo/frontend ./
RUN npm run build

# Backend runtime
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY demo/backend/server ./demo/backend/server

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    strawberry-graphql[flask] \
    torch \
    torchvision \
    opencv-python \
    numpy \
    pycocotools \
    dataclasses-json

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/dist ./demo/frontend/dist

# Expose port
EXPOSE 5000

# Run the application
WORKDIR /app/demo/backend/server
CMD ["python", "app.py"]
