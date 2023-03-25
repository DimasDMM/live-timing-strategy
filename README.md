# Live Timing Strategy

## Introduction

To do

## Development

![](./docs/cat-typing.gif)

### Setup

For development, we also need to install these tools:
- GoLang: https://go.dev/
- Python 3.9: https://www.python.org/
- (Optional) MySQL Workbench: https://www.mysql.com/products/workbench/
- (Optional) Visual Studio: https://code.visualstudio.com/

### MySQL

Docker:
```sh
docker run --name live-timing-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0.32
```

### Python

Linux:
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install tox==4.4.7 poetry==1.4.0
poetry config virtualenvs.create false
```

Windows:
```sh
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install tox==4.4.7 poetry==1.4.0
poetry config virtualenvs.create false
```

> In Windows, if there is any error similar to "running scripts is disabled",
  use this command: `Set-ExecutionPolicy Unrestricted CurrentUser`.

#### Adding more dependencies

Every time you add more dependencies, you'll need to update the lock file. For
this purpose, use this command while you are in the virtual env:
```sh
poetry lock --no-update
```

> Tip: in case that Poetry is slow to resolve the dependencies, try to clear its
  cache: `poetry cache clear --all <name>`

## Deployment

![](./docs/rocket-launch.gif)

### Setup

Before running the scripts, we need to install a few things in our system:
- Docker: https://docs.docker.com/desktop
- Minikube: https://minikube.sigs.k8s.io/docs/start/

> After installing Docker and Minikube, it may require to restart the computer.

### Kubernetes

Prepare the local kubernetes cluster with these commands:
```sh
minikube start
kubectl apply -f ./k8s/00-namespace.yaml
```

Optionally, you may run the Minikube dashboard with `minikube dashboard`.

### Kafka

Commands:
```sh
kubectl apply -f ./kafka/k8s/00-zookeeper.yaml
kubectl apply -f ./kafka/k8s/01-kafka-broker.yaml
```

Optionally, if we want to access Kafka from outside the cluster, we need to
forward the port. This command is required if you want to run the scripts
locally instead of using Kubernetes.
```sh
kubectl port-forward -n live-timing service/kafka-service 9092
```

Optionally, we may run a Kafka UI with Kouncil (use `admin` as user and pass):
```sh
kubectl apply -f ./kafka/k8s/02-kouncil.yaml
kubectl port-forward -n live-timing service/kouncil-service 8080:8080
```

### MySQL

WIP

### Live timing listener

#### Listener: Websocket

Local Python command:
```sh
python -m pyback.runners.ws_listener \
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

#### Listener: API REST

WIP

### Messages parser

WIP

### Raw storage

Local Python command:
```sh
python -m pyback.runners.raw_storage \
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

### Metrics computation

WIP

### Web: API REST

WIP

### Web: App

WIP

## Test

### Kafka

Check that Kafka works correctly with a local dummy consumer:
```sh
python -m pyback.runners.kafka_check \
  --kafka_servers localhost:9092 \
  --kafka_topic test-topic \
  --kafka_group test-group \
  --test_mode consumer \
  --verbosity 1
```

And a local dummy producer:
```sh
python -m pyback.runners.kafka_check \
  --kafka_servers localhost:9092 \
  --kafka_topic test-topic \
  --test_mode producer \
  --verbosity 1
```

Note that, if you are using a different Kafka, you may need to replace the
value of `--kafka_servers` with your list of Kafka brokers (separated) by
commas.

## Features

### Web App

Features:
- Overall view of the current status of the race.
- Estimated status of the race after doing all the pit stops.
- History of teams that entered to boxes, including:
  - The lap when they entered.
  - How many laps they did with the kart.
  - The best time in the stint.
  - The average time in the stint.
  - Using a model (statistical or ML), tag the kart depending on 
    its performance.
- If a driver enters right and changes the kart, what is the probability of
  getting a good performance kart.

## FAQs

### What is the performance of a kart?

Depending on the performance of a kart with respect to the rivals, it can be
labelled as:
- Good (green)
- Red (bad)
- Blue (unknown)

### How average time is computed?

When a driver is doing a stint, s/he might do slow laps due to external reasons.
The app excludes those laps (outliers) from the average computation. Moreover,
it only takes into account the last `5` laps (by default) in the computation.
