# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its dependencies
RUN pip install --no-cache-dir playwright && \
    playwright install-deps && \
    playwright install

# Expose port if you want to access any service from this container
# EXPOSE 8080

# Run the app.py script when the container launches
CMD ["python", "app.py"]
