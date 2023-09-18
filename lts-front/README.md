# Live Timing Strategy - App Frontend

## Introduction

App frontend to display timing information.

## Setup for development

For development, we also need to install these tools:
- PHP 8.2
- Composer: https://getcomposer.org/

### Network of containers

The containers need to be on the same network to connect to each other.
Otherwise, the API REST won't be able to see the database.
```sh
docker network create lts-network
```

### Website

Build the container:
```sh
docker build --no-cache --tag lts-website ./dockerfiles/php
```

Run it:
```sh
docker run \
  --name lts-website \
  --network lts-network \
  -p 9000:9000 \
  --env-file .env \
  lts-website
```

### Nginx (website)

> Note: The container `lts-nginx-website` must be running before running this.

Build the container:
```sh
docker build --no-cache --tag lts-website-nginx ./dockerfiles/nginx
```

Run it:
```sh
docker run \
  --name lts-website-nginx \
  --network lts-network \
  -p 8091:80 \
  lts-website-nginx
```

## Application

You can access to the main application by opening `http://localhost:8000`.

> Note: The ports depend on the settings of the file `.env`.
