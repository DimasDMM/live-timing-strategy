# CKM Timing: Backend

## Introduction

To do

## Commands

> Note: These commands have been tested only in MacOS, but they should work in Git Bash (Windows) too.

You can control the docker containers with these two commands:
```sh
sh manager.sh docker:run
sh manager.sh docker:down
```

There is an additional command to run a container with Swagger:
```sh
sh manager.sh doc:ui
```

Have fun! ᕙ (° ~ ° ~)

## Application

### API REST

The API is located at: `http://localhost:8090`.

Note that this application is documented with Swagger, which is available at: `http://localhost:8091`.

> Note: The ports depend on the settings of the file `.env`.

### MySQL database

To do

### Crawler

To do

### Data analysis

To do
