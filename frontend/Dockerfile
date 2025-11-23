# frontend/Dockerfile

# ======================================================
# Stage 1: Build the React app
# ======================================================
# Okay, first stage: build the React app.
# FIX: Upgrading to node:20-alpine for better stability and to avoid metadata issues.
FROM node:20-alpine AS build

# Let's put the app inside this directory in the container
WORKDIR /app

# Copy the package files first to leverage Docker caching for dependencies
COPY package.json ./

# Now install all the dependencies.
RUN npm install

# Copy the rest of the source code.
# Now that dependencies are installed, we're ready to copy the rest.
COPY . .

# Time to build the production assets.
# This command will create the 'build' folder with our optimized files.
RUN npm run build


# ======================================================
# Stage 2: Serve the app with a lightweight web server
# ======================================================
# Now we start a new, much smaller container for production.
# The `nginx:alpine` image is perfect for this—it's super light!
FROM nginx:alpine

# The Nginx container has its own default config. We need to replace it with ours
# to tell it how to serve our React app. This assumes you have an `nginx.conf` file
# in your frontend directory that's ready to go.
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# We need to grab the static HTML, CSS, and JS files from our 'build' stage
# and put them in the Nginx web root. The `--from=build` is the magic part!
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 so the container can be accessed.
EXPOSE 80

# This is the command that Nginx will run when the container starts.
# We're telling it to stay in the foreground so Docker can manage it.
CMD ["nginx", "-g", "daemon off;"]