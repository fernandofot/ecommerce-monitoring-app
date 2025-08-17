# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the server.js file into the container
COPY server.js .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the server
CMD ["node", "server.js"]