import logging

import kopf

from easykube import (
    Configuration,
    ApiError,
    ResourceSpec,
    resources as k8s
)

from .config import settings, Behaviour, UpdateMode


# Create an easykube client from the environment
from pydantic.json import pydantic_encoder
ekclient = Configuration.from_environment(json_encoder = pydantic_encoder).async_client()


logger = logging.getLogger(__name__)


VerticalPodAutoscaler = ResourceSpec(
    "autoscaling.k8s.io/v1",
    "verticalpodautoscalers",
    "VerticalPodAutoscaler",
    True
)


@kopf.on.cleanup()
async def on_cleanup(**kwargs):
    """
    Runs on operator shutdown.
    """
    await ekclient.aclose()


def get_annotation_enum(annotations, enum, name, default):
    """
    Gets an enum value for the given annotation.
    """
    annotation = annotations.get(name)
    if annotation:
        try:
            return enum(annotation)
        except ValueError:
            pass
    return default


@kopf.on.event(k8s.Deployment.api_version, k8s.Deployment.name)
@kopf.on.event(k8s.StatefulSet.api_version, k8s.StatefulSet.name)
@kopf.on.event(k8s.DaemonSet.api_version, k8s.DaemonSet.name)
async def workload_event(type, namespace, name, annotations, meta, body, **kwargs):
    """
    Executes when an event occurs for a workload resource.
    """
    # Any associated VPA should be deleted when the resource is deleted due to
    # ownership, so we don't need to act on delete events
    if type == "DELETED":
        return
    # Get the value of the behaviour annotation
    behaviour = get_annotation_enum(
        annotations,
        Behaviour,
        settings.behaviour_annotation,
        settings.default_behaviour
    )
    # Ensure that a VPA does or doesn't exist depending on the requested behaviour
    if behaviour == Behaviour.CREATE:
        await VerticalPodAutoscaler(ekclient).create_or_patch(
            name,
            {
                "metadata": {
                    "annotations": {
                        "app.kubernetes.io/managed-by": "auto-vpa",
                    },
                    # Add the workload as an owner reference to get cascading deletion
                    "ownerReferences": [
                        {
                            "apiVersion": body["apiVersion"],
                            "kind": body["kind"],
                            "name": name,
                            "uid": meta["uid"],
                            "controller": True,
                            "blockOwnerDeletion": True,
                        },
                    ],
                },
                "spec": {
                    "targetRef": {
                        "apiVersion": body["apiVersion"],
                        "kind": body["kind"],
                        "name": name,
                    },
                    # Use the value of the update mode annotation
                    "updatePolicy": {
                        "updateMode": get_annotation_enum(
                            annotations,
                            UpdateMode,
                            settings.update_mode_annotation,
                            settings.default_update_mode
                        ),
                    },
                },
            },
            namespace = namespace
        )
    else:
        await VerticalPodAutoscaler(ekclient).delete(name, namespace = namespace)
