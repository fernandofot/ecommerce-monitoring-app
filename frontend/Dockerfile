# frontend/Dockerfile

# Okay, first stage: build the React app.
# Using a small node image to keep the build dependencies light.
FROM node:18-alpine AS build

# Let's put our app inside this directory in the container
WORKDIR /app

# Copy the package files first. This is a crucial trick!
# It lets Docker cache this `npm install` layer if these files don't change,
# which makes rebuilding way faster.
COPY package.json ./

# Now install all the dependencies.
RUN npm install

# Copy the rest of the source code.
# Now that dependencies are installed, we're ready to copy the rest.
COPY . .

# Time to build the production assets.
# This command will create the 'build' folder.
RUN npm run build

# That's it for this stage. This container will not run anything.
# The next stage (in another Dockerfile) will grab the 'build' directory from this one.
# So, no need for a 'CMD' here.
