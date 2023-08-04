from pulumi import ComponentResource, ResourceOptions
from pulumi_kubernetes.core.v1 import (
    Namespace,
    PodTemplateSpecArgs,
    PodSpecArgs,
    ContainerArgs,
    ContainerPortArgs,
    Service,
    ServiceSpecArgs,
    ServicePortArgs,
)
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs, LabelSelectorArgs
from pulumi_kubernetes.networking.v1 import (
    Ingress,
    IngressSpecArgs,
    IngressRuleArgs,
    HTTPIngressRuleValueArgs,
    HTTPIngressPathArgs,
    IngressBackendArgs,
    IngressServiceBackendArgs,
    ServiceBackendPortArgs,
)


class ApplicationArgs:
    def __init__(
        self,
        replicas: int,
        application_name: str,
        image_uri: str,
        container_port: int,
        hostname: str,
    ):
        self.replicas = replicas
        self.application_name = application_name
        self.image_uri = image_uri
        self.container_port = container_port
        self.hostname = hostname


class Application(ComponentResource):
    def __init__(self, name: str, args: ApplicationArgs, opts: ResourceOptions = None):
        super().__init__("kubernetes:index:Application", name, {}, opts)

        opts.parent = self

        application_namespace = Namespace(f"{name}-appnamespace", opts=opts)

        app_label = {"app": args.application_name}

        application_deployment = Deployment(
            f"{name}-appdeployment",
            metadata=ObjectMetaArgs(namespace=application_namespace.metadata.name),
            spec=DeploymentSpecArgs(
                replicas=args.replicas,
                selector=LabelSelectorArgs(match_labels=app_label),
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels=app_label),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name=args.application_name,
                                image=args.image_uri,
                                ports=[
                                    ContainerPortArgs(
                                        container_port=args.container_port,
                                        host_port=8080,
                                    )
                                ],
                            )
                        ]
                    ),
                ),
            ),
            opts=opts,
        )

        application_service = Service(
            f"{name}-appservice",
            metadata=ObjectMetaArgs(namespace=application_namespace.metadata.name),
            spec=ServiceSpecArgs(
                selector=app_label,
                ports=[
                    ServicePortArgs(
                        port=80, target_port=args.container_port, name="http-port"
                    )
                ],
            ),
            opts=opts,
        )

        application_ingress = Ingress(
            f"{name}-ingress",
            metadata=ObjectMetaArgs(
                namespace=application_namespace.metadata.name,
                annotations={
                    "kubernetes.io/ingress.class": "nginx",
                },
            ),
            spec=IngressSpecArgs(
                ingress_class_name="nginx",
                rules=[
                    IngressRuleArgs(
                        host=args.hostname,
                        http=HTTPIngressRuleValueArgs(
                            paths=[
                                HTTPIngressPathArgs(
                                    path="/",
                                    path_type="ImplementationSpecific",
                                    backend=IngressBackendArgs(
                                        service=IngressServiceBackendArgs(
                                            name=application_service.metadata.name,
                                            port=ServiceBackendPortArgs(
                                                name="http-port"
                                            ),
                                        )
                                    ),
                                )
                            ]
                        ),
                    )
                ]
            ),
            opts=opts,
        )
