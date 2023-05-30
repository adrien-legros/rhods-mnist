# Rhods Mnist

## Result

![final-result.gif](./docs/gif/final-result.gif)

## Operators

### List

- [Red Hat Openshift Data Science](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-data-science)
- [Openshift Pipeline](https://docs.openshift.com/container-platform/4.13/cicd/pipelines/op-release-notes.html)
- [Openshift Serverless](https://docs.openshift.com/serverless/1.28/about/about-serverless.html)

### Installation

```shell
oc apply -k ./operators/install/
```

### Custom Resources

Wait until the operators installation to finish and run:

```shell
oc apply -k ./operators/instance/
```

## Lab deployment

```shell
oc apply -k ./manifests/
```

## Lab

### Initialization

Push the data into the previously deployed minio bucket.

```shell
oc apply -k ./lab/init/
```

### Lab instructions

[DEPRECATED] Lab instrcutions can be found [here](./docs/lab-instructions.md).

### Lab scripts

Scripts are deployed using kustomize. If you want to run the same script more than once, first run bellow command than use `oc create -f ./lab/SCRIPT/job.yaml`, replacing SCRIPT with the right directory.

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