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

# Memcached
RUN apt-get install -y zlib1g-dev && \
    apt-get install -y libmemcached-dev && \
    curl -L -o /tmp/memcached.tar.gz "https://github.com/php-memcached-dev/php-memcached/archive/php7.tar.gz" && \
    mkdir -p memcached && \
    tar -C memcached -zxvf /tmp/memcached.tar.gz --strip 1 && \
    ( \
        cd memcached && \
        phpize && \
        ./configure && \
        make -j$(nproc) && \
        make install \
    ) && \
    rm -r memcached && \
    rm /tmp/memcached.tar.gz && \
    docker-php-ext-enable memcached

# Finish dependencies installation
COPY ./php.ini /usr/local/etc/php/conf.d/php.ini

RUN echo export PATH=$PATH:./vendor/bin > $HOME/.bashrc
