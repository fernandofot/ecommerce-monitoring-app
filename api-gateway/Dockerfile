# api-gateway/Dockerfile 
# This file tells Docker how to build our API Gateway service.
# Think of it as a recipe for our container.

# We'll start with a small, efficient Node.js base image.
# The 'alpine' version is great for keeping our final image size down.
FROM node:20-alpine

# Let's set the working directory inside the container. All our
# commands will run from here.
WORKDIR /app

# We'll copy just the package files first. This lets Docker use its cache
# more effectively, so we don't have to re-install dependencies every time
# we change our server code.
COPY package*.json ./

# Now, let's install our project dependencies.
RUN npm install

# Okay, now we'll copy the actual application code into the container.
COPY server.js .

# We need to tell Docker which port our application will listen on.
# This doesn't actually publish the port, it's more of a declaration.
EXPOSE 3000

# Finally, we'll tell the container what command to run when it starts.
# It will simply execute our server file.
CMD ["node", "server.js"]
