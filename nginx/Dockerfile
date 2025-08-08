# nginx/Dockerfile

# Okay, let's start with a really small Nginx image.
# The 'alpine' version is great because it keeps the final image size minimal.
FROM nginx:alpine

# Copy our custom Nginx config file.
# This file tells Nginx where to find our frontend app's static files.
# It overwrites the default one in the container.
COPY nginx.conf /etc/nginx/nginx.conf

# Exposing the standard HTTP port.
# This makes it accessible from the host machine.
EXPOSE 80

# Finally, run Nginx. We need to make sure it runs in the foreground
# using 'daemon off;', otherwise the container will start and immediately exit.
CMD ["nginx", "-g", "daemon off;"]
