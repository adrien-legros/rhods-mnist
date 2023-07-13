# Manifests

## Bundles

Operators and instances are grouped in 3 bundles. The core bundle is required of any other.

### Core

Contains the fundamentals of the demo: create a data science environement, create a pipeline, serve your model, make live inference.

```shell
oc apply -k ./operators/core
# Wait for the operators to install
# For RHODS you can use the ./manifests/operators/wait-for-rhods.sh script
oc apply -k ./operators-instances/
oc apply -k ./instances/core
```

### Automated-pipelines

Trigger a data science pipeline from a pull request. Version your run and retrieve results.

```shell
oc apply -k ./operators/automated-pipelines
# Wait for the operators to install
oc apply -k ./instances/automated-pipelines
```

### Streaming

Batch inference. Automatically make inference for each image upload to the bucket storage. Retrieve inference on a Grafana dashboard

```shell
oc apply -k ./operators/streaming
# Wait for the operators to install
oc apply -k ./instances/streaming
```


