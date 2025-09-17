FROM php:8.2-apache

# Set the working directory
WORKDIR /var/www/html

# Copy all project files into the image's web directory
COPY . /var/www/html/

# Expose port 80 for the web server
EXPOSE 80
