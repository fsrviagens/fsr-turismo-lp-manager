FROM php:8.2-apache

# Instala as extensões PDO e PDO_PGSQL para se conectar ao PostgreSQL
RUN docker-php-ext-install pdo pdo_pgsql

# Set the working directory
WORKDIR /var/www/html

# Copy all project files into the image's web directory
COPY . /var/www/html/

# Expose port 80 for the web server
EXPOSE 80

