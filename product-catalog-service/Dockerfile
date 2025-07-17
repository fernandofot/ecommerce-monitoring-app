# Dockerfile
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
# Using --no-cache-dir to keep image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn, a fast ASGI server
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 specifies the port
# --reload (optional, for development) enables auto-reloading on code changes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
