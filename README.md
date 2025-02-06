# MLOps with Openshift AI

## About

This demo illustrates MLOps features of Openshift AI and extensions to Openshift (streaming, ELT, ...).

## Content

- Openshift AI MLOps features (notebooks, automated pipeline creation through git, experimentations, artifacts, model registry)
- Streaming with kafka
- Data transformation with camel
- Kserve features (usage of transformer for pre/post processing)

## Deployment

The following procedure will deploy all the demo components. If you want to deploy only specific components, look at [this documentation](./manifests/readme.md).

### Operators 

Install the operators.

```shell
oc apply -k ./manifests/operators/
```

Wait for the installations to complete. Confirm that all operators are ready.


### Operator instances

Deploy the data science cluster and the knative instances by runnning:

```shell
oc apply -k ./manifests/operators-instances/
```

### Demo environment.


Deploy the demo instances:

```shell
helm template ./manifests/instances/core | oc apply -f -
oc kustomize ./manifests/instances/automated-pipelines/ --enable-helm | oc apply -f -
oc kustomize ./manifests/instances/streaming/ --enable-helm | oc apply -f -

```

### Required manual setup on Openshift AI

1. Data science pipeline

Go to the digit-recognition data science project. On the pipeline tab, create a new pipeline server using one of the data connection available. Change the bucket name to "ml-pipelines" for clarity. Wait for the pipeline server creation to complete.

2. Notebook creation

Create a new workbench. Use the standard data science container image. Add the "data" data connection. Wait for the notebook creation. Open it and clone https://github.com/adrien-legros/rhods-mnist-model.

3. Model registry setup

On the settings side of Openshift AI choose model registry. Create a new one with the settings:
- Name: model-regisgtry
- Host: mysql.mnist
- Port: 3306
- Database name: modelregistry

Wait for the model registry creation to complete.

### Credentials: username / password

- Openshift AI: your openshift user (needs to be a openshift ai admin)
- Gitea: data-scientist-1 / rhods
- Grafana: admin / admin

## [UNCOMPLETE] Architecture

![global-architecture](./docs/schemas/global-architecture.png)

The schema does to reflect:
- Model registry
- Experimentations and metric tracking
- Kserve as a variation for the streaming workflow

## [DEPRECATED] Walkthrough

Deprecated but gives some steps for the demo.
Walkthourgh and highlights can be found on [this documentation](./docs/walkthrough.md).
