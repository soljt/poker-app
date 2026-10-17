FROM python:3.14-slim

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

# Run as an unprivileged user. game_data is where recorded games go; the
# compose file mounts a volume there, which starts out owned by this user.
RUN useradd --system --uid 10001 --no-create-home poker \
    && mkdir -p /app/game_data && chown poker /app/game_data
USER poker

# Ensure Flask runs in production
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the Flask port
EXPOSE 5000

# Start the app
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "run:app", "-b", "0.0.0.0:5000"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]