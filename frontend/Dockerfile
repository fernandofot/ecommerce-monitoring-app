# frontend/Dockerfile

# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json (if you have one)
# This helps leverage Docker cache if dependencies don't change
COPY package.json ./
# If you use yarn, copy yarn.lock instead: COPY yarn.lock ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app for production
# This creates the 'build' folder with static assets
RUN npm run build

# No CMD here. This image's purpose is just to create the /app/build directory.
# The 'serve' command will be run by Nginx directly mounting this build output.
# The container will exit after 'npm run build' completes.
