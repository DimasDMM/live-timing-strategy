FROM php:8.2-fpm

# Workdir
ENV WORKDIR /var/www/html
WORKDIR $WORKDIR

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl zip unzip git libicu-dev && \
    apt-get install -y mariadb-server mariadb-server-core default-mysql-server default-mysql-server-core && \
    pecl install xdebug && \
    apt-get install -y apt-utils autoconf build-essential curl git libssl-dev unzip vim zip gnupg wget

# Commands to install Composer in the container
#RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
#    php -r "if (hash_file('sha384', 'composer-setup.php') === 'e21205b207c3ff031906575712edab6f13eb0b361f2085f1f1237b7126d785e826a450292b6cfd1d64d92e6563bbde02') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" && \
#    php composer-setup.php && \
#    mv composer.phar /usr/bin/composer && \
#    php -r "unlink('composer-setup.php');"

RUN docker-php-ext-install mysqli pdo pdo_mysql dba intl && \
    docker-php-ext-enable xdebug

# Finish dependencies installation
COPY ./php.ini /usr/local/etc/php/conf.d/php.ini

RUN echo export PATH=$PATH:./vendor/bin > $HOME/.bashrc
