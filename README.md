**Data Pipelines** ![Coverage badge](./lts-pipeline/docs/coverage.svg) | **API REST** ![Coverage badge](./lts-api/docs/coverage.svg)

# Live Timing Strategy

## Introduction

Full stack application for live timing analysis.

## Development

![](./docs/images/cat-typing.gif)

This project is composed by several parts, and each of them require a different
setup. For further details:
- [API REST](./lts-api/README.md)
- [App Frontend](./lts-front/README.md)
- [Data Pipelines](./lts-pipeline/README.md)

## Deployment

![](./docs/images/rocket-launch.gif)

### Setup

Before running the scripts, we need to install a few things in our system:
- Docker: https://docs.docker.com/desktop
- Minikube: https://minikube.sigs.k8s.io/docs/images/start/
- Kafka CLI: https://kafka.apache.org/downloads

> After installing Docker and Minikube, it may require to restart the computer.

### Kubernetes

Start Minikube:
```sh
minikube start
```

Optionally, we may run the Minikube dashboard with `minikube dashboard`.

### Kafka

Commands:
```sh
kubectl apply -f ./k8s/kafka/00-zookeeper.yaml
kubectl apply -f ./k8s/kafka/01-kafka-broker.yaml
```

Optionally, if we want to access Kafka from outside the cluster, we need to
forward the port. This command is required if we want to run the scripts
locally instead of using Kubernetes.
```sh
kubectl port-forward -n default service/kafka-service 9092
```

Optionally, we may run a Kafka UI with Kouncil (use `admin` as user and pass):
```sh
kubectl apply -f ./k8s/kafka/02-kouncil.yaml
kubectl port-forward -n default service/kouncil-service 8080:8080
```

#### Setup topics

Topic for notifications:
```sh
kafka-topics --create --bootstrap-server localhost:9092 --partitions 1 --topic notifications
```

To delete all topics:
```sh
kafka-topics --delete --bootstrap-server localhost:9092 --topic notifications
```

### MySQL

WIP

### Pipeline

WIP

### Web: API REST

WIP

### Web: App

WIP

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

### How the average time is computed?

When a driver is doing a stint, it might do slow laps due to external reasons.
The app excludes those laps (outliers) from the average computation. Moreover,
it only takes into account the last `5` laps (by default) in the computation.

---

Have fun! ᕙ (° ~ ° ~)
