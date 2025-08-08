# Dockerfile

# Start with a good, lightweight Python base image.
# The 'slim-buster' variant is perfect for keeping the final image size down.
FROM python:3.9-slim-buster

# Let's set the working directory inside the container.
WORKDIR /app

# This is a key trick for Docker caching!
# Copy the requirements file first so we only reinstall dependencies if they change.
COPY requirements.txt .

# Install our project's dependencies.
# The '--no-cache-dir' option is a nice touch to keep the image even smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Now that the dependencies are installed, we can copy the rest of our code.
# This makes sure the previous layer is cached if we're just making code changes.
COPY . .

# Just letting Docker know that our app will be listening on this port.
EXPOSE 8000

# This is the command that actually runs the backend.
# We're using Uvicorn with FastAPI.
# The '--host 0.0.0.0' part is super important so it's accessible from outside the container.
# We'll skip '--reload' since this is a production-ready container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
