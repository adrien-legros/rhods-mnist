# Rhods Mnist

## About

This git repository aims to demonstrates how to leverage Red Hat Openshift Data Science (RHODS) to:
- Setup a data science environment
- Create and run a deep learning model
- Create a data science pipeine for reproducibility
- Run, see and compare the outputs
- Serve your model to make it accessible to applications
- Deploy an application to interact with your model and make predictions

This readme provides commands to deploy the lab. There are also few jobs that enables you to initialize, solve or reset the lab. You will also find in the docs the [lab instructions](./docs/lab-instructions.md) with step by step explanations.

## Result

![final-result.gif](./docs/gif/final-result.gif)

## Installation

### Operators list

- [Red Hat Openshift Data Science 1.26](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-data-science)
- [Openshift Pipeline](https://docs.openshift.com/container-platform/4.13/cicd/pipelines/op-release-notes.html)
- [Openshift Serverless](https://docs.openshift.com/serverless/1.28/about/about-serverless.html)

### Operators installation

```shell
oc apply -k ./operators/install/
```

### Enable Knative serving

Wait until the operators installation to finish and run:

```shell
# Wait for the serverless operator to deploy
oc -n openshift-serverless wait --for=condition=Ready=true po -l name=knative-openshift --timeout=5m
# Instanciate Serving
oc apply -k ./operators/instance/
```

## Lab deployment

```shell
# Wait for RHODS Operator and deployments
oc -n redhat-ods-operator wait --for=condition=Ready=true po -l name=rhods-operator --timeout=10m
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=model-mesh --timeout=10m
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l control-plane=controller-manager --timeout=10m
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l control-plane=odh-model-controller --timeout=10m
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=notebook-controller --timeout=10m
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=rhods-dashboard --timeout=10m

# Setup the environement
oc apply -k ./manifests/
```

## Lab

### Initialization

Initialisation in mandatory. It pushes the data used by notebooks into a minio S3 bucket.

```shell
oc apply -k ./lab/init/
```

### Lab instructions

Lab instrcutions can be found [here](./docs/lab-instructions.md).

### Lab scripts

Scripts are deployed using kustomize. If you want to run the same script more than once, first delete the completed job using `oc delete -n mnist job <SCRIPT_NAME>`. Replace SCRIPT_NAME with *lab-solve* or *lab-reset*.

#### Solve

```shell
oc apply -k ./lab/solve/
```

#### Reset

```shell
oc apply -k ./lab/reset/
```

## Inference

Deploy the web application for drawing as well as the servless function to transform inference data.

```shell
oc apply -k ./inference/
```