# Live Timing Strategy - Pipeline

## Introduction

Retrieves and analyses the data that comes from a live timing application.

## Setup for development

For development, we also need to install these tools:
- Python 3.9: https://www.python.org/
- (Optional) Visual Studio: https://code.visualstudio.com/

Linux:
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install tox==3.28 poetry==1.4.2
poetry config virtualenvs.create false
```

Windows:
```sh
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install tox==3.28 poetry==1.4.2
poetry config virtualenvs.create false
```

> In Windows, if there is any error similar to "running scripts is disabled",
  use this command: `Set-ExecutionPolicy Unrestricted CurrentUser`.

### Adding more dependencies

Every time we add more dependencies, we'll need to update the lock file. For
this purpose, use this command while we are in the virtual env:
```sh
poetry lock --no-update
```

> Tip: in case that Poetry is slow to resolve the dependencies, try to clear its
  cache: `poetry cache clear --all <name>`

## Pipeline

### Pipeline: Websocket

Local Python command:
```sh
python -m ltspipe.runners.ws_listener \
  --kafka_servers localhost:9092 \
  --websocket_uri ws://www.apex-timing.com:8092 \
  --verbosity 1
```

Arguments:
- `--kafka_servers`: (**mandatory**) List of Kafka brokers separated by commas.
  Example: `localhost:9092,localhost:9093`.
- `--kafka_topic`: (optional) Topic of Kafka to write messages. By default,
  it is `raw-messages`.
- `--websocket_uri`: (**mandatory**) Websocket URI to listen for incoming data.
  Example: `ws://www.apex-timing.com:8092`.
- `--verbosity`: (optional) Level of verbosity of messages. The values can be
  `0` to disable messages, `1` for debug (or greater), `2` for info (or
  greater), ... and `5` for critical. By default, it is `2`.

### Pipeline: API REST

WIP

### Pipeline: Messages parser

WIP

### Pipeline: Raw storage

Local Python command:
```sh
python -m ltspipe.runners.raw_storage \
  --kafka_servers localhost:9092 \
  --verbosity 1
```

Arguments:
- `--kafka_servers`: (**mandatory**) List of Kafka brokers separated by commas.
  Example: `localhost:9092,localhost:9093`.
- `--kafka_topic`: (optional) Topic of Kafka to suscribe. By default, it is
  `raw-messages`.
- `--kafka_group`: (optional) Suscribe to the topic with a specific group name. 
  By default, it is `raw-storage`.
- `--output_path`: (optional) Path to store the raw data. By default, it is
  `./artifacts/logs`.
- `--verbosity`: (optional) Level of verbosity of messages. The values can be
  `0` to disable messages, `1` for debug (or greater), `2` for info (or
  greater), ... and `5` for critical. By default, it is `2`.

> Local GO command (WIP):
> ```sh
> go run . \
>   -mode raw_storage \
>   -output_path ./artifacts \
>   -bootstrap_servers localhost:9092
> ```

### Pipeline: Metrics computation

WIP

## Test

### Kafka

Check that Kafka works correctly with a local dummy consumer:
```sh
python -m ltspipe.runners.kafka_check \
  --kafka_servers localhost:9092 \
  --kafka_topic test-topic \
  --kafka_group test-group \
  --test_mode consumer \
  --verbosity 1
```

And a local dummy producer:
```sh
python -m ltspipe.runners.kafka_check \
  --kafka_servers localhost:9092 \
  --kafka_topic test-topic \
  --test_mode producer \
  --verbosity 1
```

Note that, if we are using a different Kafka, we may need to replace the
value of `--kafka_servers` with our list of Kafka brokers (separated) by
commas.
