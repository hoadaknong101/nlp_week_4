# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for build cache)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn (if not already in requirements.txt)
RUN pip install gunicorn

# Copy project files
COPY . .

# Expose the port Gunicorn will listen on
EXPOSE 5000

# Start Gunicorn (bind to all interfaces, 4 worker processes)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
