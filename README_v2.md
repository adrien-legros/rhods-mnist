## Fondations

### Installation

```shell
oc apply -k ./operators/install/
```

### Operators Custom Resources

Wait until the operators installation finish.

```shell
oc apply -k ./operators/instance/
```

## Lab deployment

```shell
oc apply -k ./manifests/
```

## Lab

### Lab instructions

### Lab scripts

#### Init

```shell
oc apply -k ./lab/init/
```

#### Solve

```shell
oc apply -k ./lab/solve/
```

#### Reset

```shell
oc apply -k ./lab/reset/
```