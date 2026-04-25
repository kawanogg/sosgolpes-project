FROM php:8.2-apache

RUN apt-get update && apt-get install -y \
    libssl-dev \
    libcurl4-openssl-dev \
    openssl \
    dos2unix \
    && docker-php-ext-install pdo pdo_mysql curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

WORKDIR /var/www/html

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

COPY main/views/index.html /var/www/html/index.html

RUN chown -R www-data:www-data /var/www/html

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
