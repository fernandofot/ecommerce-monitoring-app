# nginx/Dockerfile
FROM nginx:alpine

# Copy custom Nginx config to replace the main Nginx config file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 (Nginx's internal listening port)
EXPOSE 80

# The default Nginx CMD will run the server
CMD ["nginx", "-g", "daemon off;"]
    