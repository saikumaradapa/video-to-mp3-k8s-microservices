# 🎧 Video-to-MP3 — Microservices (Python, RabbitMQ, Docker, Kubernetes)

- A Scalable Microservices Platform for Video to MP3 Conversion Using Python, RabbitMQ, Docker, and Kubernetes.
- Focused on designing microservice architecture.

## TL;DR

- Upload a video to `gateway` → `gateway` publishes a RabbitMQ job → `converter` converts video → `notification` notifies.
- Primary folders: `src/*` (services + manifests), `cluster/manifests` (namespace & policies), `Makefile` (apply/delete helpers).

## Important services

- gateway — HTTP API for uploads and job creation
- auth — authentication/authorization
- converter — worker that converts video to MP3 (uses FFmpeg)
- notification — sends completion emails

Infra: `rabbitmq`, `mysql`, `mongodb`, `mailhog`

## Repo layout

- `cluster/manifests/` — namespace, limit-range, resource-quota
- `src/<service>/` — service code, `Dockerfile`, `requirements.txt`, `manifests/`
- `Makefile` — orchestration convenience targets

## Makefile

Used `Makefile` to run/manage manifests (works on PowerShell/CMD):

```powershell
make ns-up        # create namespace and cluster policies
make apply        # apply all service manifests
make delete       # delete all service manifests
make apply-gateway  # apply manifests for gateway only
make delete-gateway # delete manifests for gateway only
make ns-delete    # remove namespace and policies
```


## Build & push images

Build images from each `src/<service>` directory and push to your registry. Update manifests' image fields before deploying.

```powershell
docker build -t <registry>/gateway:latest ./src/gateway
docker push <registry>/gateway:latest
```

## Deployment:
- designed to deploy on AWS EKS, also works on Minikube, Kind, Docker Desktop K8s. 


## Config & secrets

Replace default placeholders in `src/*/manifests/secret.yaml` and `configmap.yaml`. 
