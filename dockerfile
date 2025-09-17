FROM php:8.2-apache

# Instala as dependências necessárias para o driver do PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev

# Instala as extensões PDO e PDO_PGSQL para se conectar ao PostgreSQL
RUN docker-php-ext-install pdo pdo_pgsql

# Habilita o módulo de reescrita de URL do Apache
RUN a2enmod rewrite

# Set the working directory
WORKDIR /var/www/html

# Copia o arquivo .htaccess para o servidor
COPY .htaccess /var/www/html/

# Copy all project files into the image's web directory
COPY . /var/www/html/

# Expose port 80 for the web server
EXPOSE 80


