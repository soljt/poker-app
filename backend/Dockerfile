FROM python:3.11-slim

# Install security updates and clean up
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Ensure Flask runs in production
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the Flask port
EXPOSE 5000

# Start the app
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "run:app", "-b", "0.0.0.0:5000"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]