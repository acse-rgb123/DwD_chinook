# Use the official Nginx image
FROM nginx:alpine

# Copy static files to the nginx HTML folder
COPY static /usr/share/nginx/html/static
COPY templates /usr/share/nginx/html/templates
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 for the frontend
EXPOSE 80

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]
