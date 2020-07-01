FROM php:7.2-fpm

# Workdir
ENV WORKDIR /var/www/html
WORKDIR $WORKDIR

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl zip unzip git libicu-dev && \
    apt-get install -y mariadb-server-10.3 mariadb-server-core-10.3 default-mysql-server default-mysql-server-core && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    pecl install xdebug-2.7.2 && \
    apt-get install -y apt-utils autoconf build-essential curl git libssl-dev unzip vim zip gnupg wget

RUN docker-php-ext-install mysqli pdo pdo_mysql dba intl && \
    docker-php-ext-enable xdebug

# Finish dependencies installation
COPY ./container-dependencies.sh $WORKDIR/container-dependencies.sh
RUN bash $WORKDIR/container-dependencies.sh

RUN echo export PATH=$PATH:./vendor/bin > $HOME/.bashrc
