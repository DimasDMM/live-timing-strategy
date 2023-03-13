# CKM Timing

## Introduction

To do

## Development

### Setup

For development, we also need to install these tools:
- GoLang: https://go.dev/
- (Optional) MySQL Workbench: https://www.mysql.com/products/workbench/
- (Optional) Visual Studio: https://code.visualstudio.com/

## Deployment

### Setup

Before running the scripts, we need to install a few things in our system:
- Docker: https://docs.docker.com/desktop
- Minikube: https://minikube.sigs.k8s.io/docs/start/

> After installing Docker and Minikube, it may require to restart the computer.

### Kafka

Commands:
```sh
kubectl apply -f ./kafka/k8s/00-zookeeper.yaml
kubectl apply -f ./kafka/k8s/01-kafka-broker.yaml
```

### Live timing listener

WIP

### Messages parser

WIP

### Raw storage

WIP

### Metrics computation

WIP

### API REST

WIP

### Web app

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

### How average time is computed?

When a driver is doing a stint, s/he might do slow laps due to external reasons.
The app excludes those laps (outliers) from the average computation. Moreover,
it only takes into account the last `5` laps (by default) in the computation.
