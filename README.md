# An MLOPS journey

## Table of content

1. [About](#about)
2. [User story](#user-story)
3. [Architecture](#architecture)
4. [Highlights](#highlights)
5. [Use as a lab](#use-as-a-lab)
6. [Deployment](#deployment)

## About

This demo demonstrates an end to end automated MLOps approach for model training and serving. It leverages Red Hat Openshift Data Science (RHODS) as well as other products from Red Hat portfolio. 

## User story

A data scientist setup his Jupyter envrionement and develops his model. Once statisfied he commits his code and makes a pull request to merge into the production branch. He wants to train and deploy his model in production. The pull request automatically triggers a data science pipeline. During the training process, the model is tagged and stored into a bucket storage. A model server is serving this model and reconciles whenerer it is updated. The new model is automatically served and is consumable through api requests. It becomes a scalable model that can be used for live inference or batch streaming.

## Architecture

![global-architecture](./docs/schemas/global-architecture.png)

## Highlights

Non exhaustive list of highlights you can show using this demo:

- Data Science Envrionement
    - Setup a data science environment configuring Jupyter Notebooks
    - Create and run a machine learning model
    - Create a data science pipeine for reproducibility
- Data science pipeline
    - Run, see and compare the outputs
    - Create and run a pipeline from elyra GUI
    - Commit you code to git and create a pull request to start the automated worflow
- Model server
    - Serve your model
    - Deploy a pre-processing serverless function for the inference
    - Batch inference
    - Online inference with a frontend
- Streaming
    - Add Camel integrations to automate the batch inference
    - Grafana dashboard to watch the batch inference results

## Use as a lab

This demo might be used as a lab. Some instructions that do not contain the streaming features yet are [available here](./docs/lab-instructions.md). There are also [lab jobs](./lab/) that can be use to initialize, reset or complete the lab. Thoses jobs only works on the RHODS data science for now.

## Deployment

1. Install the operators. Some of them (typically RHODS) might require your manual approval. Go to the Openshift console and approve them.
```shell
oc apply -k ./operators/
```
2. Wait for the installations to complete. Confirm that all operators are ready with the screenshot. Confirm that the RHODS operator finished all the pod deployments with the command line.  

![operators-validation](./docs/screenshots/operators-validation.png)
```shell
chmod +x ./lab/solve/scripts/wait-for-rhods.sh
./lab/solve/scripts/wait-for-rhods.sh
```
3. Deploy the manifests.
```shell
oc apply -k ./manifests/
```
4. Configure data science project (notebooks + serving).

This job will push the datasets into your object storage.
```shell
oc apply -k ./lab/init/
```
5. Deploy MLFlow

The [helm cli](https://helm.sh/docs/intro/install/) has to be installed. Then run the script.
```shell
helm repo add strangiato https://strangiato.github.io/helm-charts/
helm repo update
helm upgrade -i mlflow-server --create-namespace --namespace mlflow strangiato/mlflow-server --values ./manifests/mlflow/values.yaml
```

6. Configure gitea
7. Configure DB

### Operators list

#### Core demo

- [Red Hat Openshift Data Science](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-data-science)
- [Openshift Pipeline](https://docs.openshift.com/container-platform/4.13/cicd/pipelines/op-release-notes.html)
- [Openshift Serverless](https://docs.openshift.com/serverless/1.28/about/about-serverless.html)

#### MLOps automation

#### Streaming



### Enable Knative serving

Wait until the operators installation to finish and run:

```shell
# Instanciate Serving
oc apply -k ./operators/instance/
```

### Mlflow

