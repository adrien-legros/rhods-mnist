# Custom Notebook Image

We need to build a custom notebook image for this demo due to Telsa P6 Nvidia GPU hardware.

## Repository

Image: quay.io/alegros/notebook:cuda-jupyter-custom-mnist-ubi8-python-3.8  
Digest: 43d9ae25f7c19bd79091e92f7859b30da9ca2671891a4fae8f89315d7a6bcc1c

## Important packages and library versions

- Cuda 11.4
- CUDDN 8.2.4
- Tensorflow 2.11.0

## Build image on OCP

```shell
oc new-build --strategy docker --binary --name custom-notebook-build
oc start-build --from-dir ./ custom-notebook-build
```