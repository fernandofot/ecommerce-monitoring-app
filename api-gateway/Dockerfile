# api-gateway/Dockerfile
# This file is the recipe for building our API Gateway container.
# It's a series of steps that tells Docker how to set up our service.

# We'll start with a lightweight and fast Node.js base image.
# The 'alpine' version is perfect for keeping our final image size small.
FROM node:20-alpine

# First, let's set the working directory. All the magic happens here!
WORKDIR /app

# We need a small tool for our health check, so let's install curl.
# This uses Alpine Linux's package manager, `apk`.
RUN apk add --no-cache curl

# To speed things up, we'll copy the package files first.
# This lets Docker intelligently use its cache, so we don't have to
# re-install dependencies if we only change the application code.
COPY package*.json ./

# Now, let's grab all our project dependencies.
RUN npm install

# After installing dependencies, we'll copy the rest of our application code.
# This is our actual `server.js` file.
COPY server.js .

# Let's set up a health check! This tells Docker how to know if
# our service is actually up and running and ready for traffic.
# It just tries to hit our server's root path.
HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD [ "curl", "-f", "http://localhost:3000" ]

# We need to expose the port our server listens on.
# This is like declaring "Hey, I'm listening here!"
EXPOSE 3000

# Last but not least, we'll define the command to start our server.
# This is what runs when the container first starts up.
CMD ["node", "server.js"]
