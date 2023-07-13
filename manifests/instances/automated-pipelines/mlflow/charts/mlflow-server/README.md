# mlflow-server

A Helm chart for deploying mlflow on OpenShift

![Version: 0.5.7](https://img.shields.io/badge/Version-0.5.7-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 2.0](https://img.shields.io/badge/AppVersion-2.0-informational?style=flat-square)

## Pre-Reqs

This chart utilizes components from the Crunch Postgres Operator and OpenShift Data Foundations in the default configuration.  The chart expects both operators to be installed on the cluster prior to deploying.

## Installing the Chart

To access charts from this from the cli repository add it:

```sh
helm repo add strangiato https://strangiato.github.io/helm-charts/
helm repo update
helm upgrade -i [release-name] strangiato/mlflow-server
```

To include a chart from this repository in an umbrella chart, include it in your dependencies in your `Chart.yaml` file.

```yaml
apiVersion: v2
name: example-chart
description: A Helm chart for Kubernetes
type: application

version: 0.1.0

appVersion: "1.16.0"

dependencies:
  - name: "mlflow-server"
    version: "0.5.7"
    repository: "https://strangiato.github.io/helm-charts/"
```

## Source Code

* <https://github.com/strangiato/helm-charts/tree/main/charts/mlflow-server>
* <https://github.com/strangiato/mlflow-server>

## Requirements

Kubernetes: `>= 1.21.0`

| Repository | Name | Version |
|------------|------|---------|
| https://strangiato.github.io/helm-charts/ | postgrescluster | 0.2.2 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Affinity configuration for the MLFlow Server pod |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| crunchyPostgres.enabled | bool | `true` | Enable creation of a postgres instance using crunchyPostgres operator |
| database.migration.enabled | bool | `false` |  |
| fullnameOverride | string | `""` | String to fully override fullname template |
| image.pullPolicy | string | `"IfNotPresent"` | The docker image pull policy |
| image.repository | string | `"quay.io/troyer/mlflow-server"` | The image repository to use |
| image.tag | string | Chart appVersion | The image tag to use |
| imagePullSecrets | list | `[]` | The image pull secret for the image repository |
| ingress.annotations | object | `{}` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths | list | `[]` |  |
| ingress.tls | list | `[]` |  |
| nameOverride | string | `""` | String to partially override fullname template (will maintain the release name) |
| nodeSelector | object | `{}` | Node selector for the MlFlow Server pod |
| objectStorage.mlflowBucketName | string | `"mlflow"` | Name of the s3 bucket if the objectBucketClaim is disabled |
| objectStorage.objectBucketClaim.annotations | object | `{}` | Additional custom annotations for the objectBucketClaim |
| objectStorage.objectBucketClaim.bucketclass | string | `"noobaa-default-bucket-class"` | BucketClass name for the creation of the objectBucketClaim |
| objectStorage.objectBucketClaim.enabled | bool | `true` | Enable creation of s3 bucket with objectBucketClaim for artifact storage |
| objectStorage.objectBucketClaim.storageClassName | string | `"openshift-storage.noobaa.io"` | StorageClassName for creation of the objectBucketClaim |
| objectStorage.s3AccessKeyId | string | `""` | S3 Access Key ID if the objectBucketClaim is disabled |
| objectStorage.s3EndpointUrl | string | `""` | URL for s3 endpoint if the objectBucketClaim is disabled |
| objectStorage.s3SecretAccessKey | string | `""` | S3 Secret Access Key if the objectBucketClaim is disabled |
| odhApplication.enabled | bool | `false` | Enable the ODH Dashboard Application tile for MLFlow |
| odhApplication.namespaceOverride | string | `""` | Used to specify the namespace ODH is installed in if installed in a different namespace from MLFlow |
| openshiftOauth.enableBearerTokenAccess | bool | `false` | Enable access to MLFlow using an OpenShift Bearer Token.  This feature enables users from outside of the cluster to read/write to MLFlow using the API.   Warning: This feature requires cluster admin to install. |
| openshiftOauth.enabled | bool | `true` | Secures MLFlow with OpenShift Oauth Proxy.  If disabling this option it is recommended to set `route.tls.termination: edge`. |
| openshiftOauth.resources | object | `{}` |  |
| podAnnotations | object | `{}` | Map of annotations to add to the pods |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` | replicas of MLFlow Server |
| resources | object | `{}` | Resource configuration for the MLFlow Server pod |
| route.annotations | object | `{}` | Additional custom annotations for the route |
| route.enabled | bool | `true` | Enable creation of the OpenShift Route object |
| route.host | string | Set by OpenShift | The hostname for the route |
| route.path | string | `""` | The path for the OpenShift route |
| route.tls.enabled | bool | `true` | Enable secure route settings |
| route.tls.insecureEdgeTerminationPolicy | string | `"Redirect"` | Insecure route termination policy |
| route.tls.termination | string | `"reencrypt"` | Secure route termination policy |
| securityContext | object | `{}` |  |
| service.port | int | `8080` | MLFlow server port |
| service.type | string | `"ClusterIP"` | Kubernetes Service type |
| serviceAccount.annotations | object | `{}` | Additional custom annotations for the ServiceAccount |
| serviceAccount.create | bool | `true` | Enable creation of ServiceAccount for MLFlow Server pod |
| serviceAccount.name | string | fullname template | The name of the ServiceAccount to use. |
| tolerations | list | `[]` | Tolerations for the MLFlow Server pod |
| trainingTestImage.pullPolicy | string | `"IfNotPresent"` | The docker image pull policy |
| trainingTestImage.repository | string | `"quay.io/troyer/mlflow-server-training-test"` | The image repository used for the helm training test |
| trainingTestImage.tag | string | Chart appVersion | The image tag to use |

## Usage

### Utilizing MLFlow from Outside the Cluster with OAuth

When accessing MLFlow from outside of the cluster with OAuth enabled, the route is secured by an OpenShift OAuth Proxy.  This OAuth proxy by default will only allow users to access MLFlow using the UI. 

If you wish to run training processes from outside of the cluster that write to MLFlow you must set `enableBearerTokenAccess: true`.  This option requires additional permissions to be granted to the MLFlow Service Account which requires cluster admin privileges.  To install mlflow-server with this feature, run the following command:

```sh
helm upgrade -i [release-name] strangiato/mlflow-server --set openshiftOauth.enableBearerTokenAccess=true
```

Once this option is enabled you can set the following environment variable in your training environment and MLFlow will automatically pass your Bearer Token to the OpenShift OAuth Proxy and authenticate any API calls MLFlow makes to the server.

```
MLFLOW_TRACKING_TOKEN=[my-token]
```

To retrieve your token from openshift run the following command:

```sh
oc whoami --show-token
```

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.11.0](https://github.com/norwoodj/helm-docs/releases/v1.11.0)
