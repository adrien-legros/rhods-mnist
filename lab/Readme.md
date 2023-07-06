## Lab deployment

```shell
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