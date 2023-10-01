# Live Timing Strategy - API REST

## Introduction

API REST to manage and read the data from the database.

## Setup for development

For development, we also need to install these tools:
- Python 3.9 or greater: https://www.python.org/
- (Optional) MySQL Workbench: https://www.mysql.com/products/workbench/
- (Optional) Visual Studio: https://code.visualstudio.com/

Linux:
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install tox==4.11 poetry==1.6.1
poetry config virtualenvs.create false
```

Windows:
```sh
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install tox==4.11 poetry==1.6.1
poetry config virtualenvs.create false
```

> In Windows, if there is any error similar to "running scripts is disabled",
  use this command: `Set-ExecutionPolicy Unrestricted CurrentUser`.

### Environment variables

There is a file with some environment variables located at `.env`. The
value `DB_HOST` changes depending on we are running the code locally or in a
container:
- Locally: `127.0.0.1`
- In docker: `lts-mysql`

To import the environment variables, we may run this command in Linux:
```sh
source .env.local
```

In Windows, we have to use this command instead of `source .env.local`:
```sh
Get-Content .env.local | foreach {
  $name, $value = $_.split('=')
  if (![string]::IsNullOrWhiteSpace($name) -and !$name.Contains('#')) {
    Set-Content Env:\$name $value
  }
}
```

### Network of containers

The containers need to be on the same network to connect to each other.
Otherwise, the API REST won't be able to see the database.
```sh
docker network create lts-network
```

### MySQL

Initialize the database with this command:
```sh
docker run \
  --name lts-mysql \
  --network lts-network \
  -p ${DB_PORT}:3306 \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0.32
```

Then, access to the database (we may use the MySQL workbench for this purpose)
and create a database with these SQL statements:
```sql
CREATE DATABASE	IF NOT EXISTS `live-timing`;
USE `live-timing`;
```

Finally, import the file [initial_tables.sql](./data/initial_tables.sql).

### API REST

Build the container:
```sh
docker build --no-cache --tag lts-api .
```

Run it:
```sh
docker run \
  --env-file .env.indocker \
  --name lts-api \
  --network lts-network \
  --env DEBUG=1 \
  -p 8090:80 \
  lts-api
```

> Note 1: the environment variables file is `.env.indocker` to run the
  container.

> Note 2: The above command has `DEBUG=1`, so the output of the API REST is
  more verbose when we are implementing new code.

Once the container is running, we may see all the available endpoints at
[http://127.0.0.1/docs](http://127.0.0.1/docs). Additionally, we may import the
Postman's template located at `./data/postman.json`.

## Tests

The tests require that we initialize a MySQL server first (see command in
the section above). Remember that we must import the environment variables
before running the tests.

Then, we may run the whole test pipeline (unit tests and code style) with the
usual command:
```sh
tox
```

We may generate the coverage report (and pass the unit tests) with this command:
```sh
poe coverage
```

## Other resources

- FastAPI: https://fastapi.tiangolo.com/
- NGinx Unit: https://unit.nginx.org/
  - Howto with FastAPI: https://unit.nginx.org/howto/fastapi/
