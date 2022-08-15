# auto-vpa

This project implements a very simple Kubernetes controller manager that can
automatically create corresponding
[VerticalPodAutoscaler (VPA)](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
resources when workload resources - `Deployment`, `DaemonSet` and `StatefulSet` - are
deployed to the cluster.

## Installation

The controller manager is deployed using [Helm](https://helm.sh/):

```sh
helm repo add auto-vpa https://stackhpc.github.io/auto-vpa
helm upgrade auto-vpa auto-vpa/auto-vpa -i
```

## Usage

The behaviour is controlled by an annotation on the workload resource, e.g.:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
  annotations:
    auto-vpa.stackhpc.com/behaviour: Create | Ignore
spec:
  # ...
```

When the annotation is set to `Create`, the controller manager will ensure that a
VPA resource exists for the deployment. If the annotation is set to `Ignore`, the
controller manager ensures that there is no VPA resource for the deployment.

If the annotation is not supplied, a default behaviour is applied. Unless configured
otherwise, the default behaviour is `Create` - this means that *every* workload resource
will get a corresponding VPA resource, even if the annotation is not present, unless it
opts out by specifying the annotation with a value of `Ignore`.

The default behaviour can be changed to `Ignore` using the Helm values:

```yaml
config:
  defaultBehaviour: Ignore
```

With this setting, VPA resources will only be created for workload resources that
opt in by specifying the annotation with a value of `Create`.
