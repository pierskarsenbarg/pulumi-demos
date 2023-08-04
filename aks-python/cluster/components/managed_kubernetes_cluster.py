from pulumi import ComponentResource, ResourceOptions, Output, Input
from pulumi_kubernetes import Provider
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs
from pulumi_kubernetes.core.v1 import Service
from components.kubernetes_cluster import (
    KubernetesCluster,
    KubernetesClusterArgs
)


class ManagedKubernetesClusterArgs(KubernetesClusterArgs):
    def __init__(
        self,
        kubernetes_version: str,
        resource_group_name: str,
        node_count: int,
        vnet_id: str,
        subnet_id: str,
        subscription_id: str,
    ):

        self.kubernetes_version = kubernetes_version
        self.resource_group_name = resource_group_name
        self.node_count = node_count
        self.vnet_id = vnet_id
        self.subnet_id = subnet_id
        self.subscription_id = subscription_id


class ManagedKubernetesCluster(ComponentResource):
    ingress_ip_address: Output[str]
    k8s_provider: Provider
    kube_config: Output[str]

    def __init__(
        self,
        name: str,
        args: ManagedKubernetesClusterArgs,
        opts: ResourceOptions = None,
    ):
        super().__init__("kubernetes:index:Managedcluster", name, {}, opts)

        cluster = KubernetesCluster(
            f"{name}-managedcluster",
            args=KubernetesClusterArgs(
                kubernetes_version=args.kubernetes_version,
                node_count=args.node_count,
                resource_group_name=args.resource_group_name,
                vnet_id=args.vnet_id,
                subnet_id=args.subnet_id,
                subscription_id=args.subscription_id,
            ),
            opts=ResourceOptions(parent=self),
        )

        nginx_ingress = Release(
            f"nginxingress",
            repository_opts=RepositoryOptsArgs(
                repo="https://kubernetes.github.io/ingress-nginx"
            ),
            chart="ingress-nginx",
            version="4.0.16",
            skip_await=False,
            values={
                "controller": {
                    "service": {
                        "externalTrafficPolicy": "Local"
                    },
                    "replicaCount": 1,
                    "nodeSelector": {"beta.kubernetes.io/os": "linux"},
                    "admissionWebhooks": {
                        "patch": {"nodeSelector": {"beta.kubernetes.io/os": "linux"}}
                    },
                },
                "defaultBackend": {"nodeSelector": {"beta.kubernetes.io/os": "linux"}},
            },
            opts=ResourceOptions(parent=self, provider=cluster.k8sProvider),
        )
        nginx_ingress_service = Service.get(
            "ingress-svc",
            Output.concat(
                nginx_ingress.status.namespace,
                "/",
                nginx_ingress.status.name,
                "-ingress-nginx-controller",
            ),
            opts=ResourceOptions(provider=cluster.k8sProvider, parent=self),
        )

        self.ingress_ip_address = nginx_ingress_service.status.load_balancer.ingress[
            0
        ].ip
        self.k8s_provider = cluster.k8sProvider
        self.kube_config = cluster.kube_config

        self.register_outputs(
            {
                "ingress_ip_address": self.ingress_ip_address,
                "k8s_provider": self.k8s_provider,
                "kube_config": self.kube_config
            }
        )
