from pulumi_azure_native import containerservice, managedidentity, authorization
from pulumi import ComponentResource, ResourceOptions, Output, Input
from pulumi_kubernetes import Provider
from typing import Any, Mapping
import base64


class KubernetesClusterArgs:
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


class KubernetesCluster(ComponentResource):
    cluster: containerservice.ManagedCluster
    kube_config: Output[str]

    def __init__(
        self, name: str, args: KubernetesClusterArgs, opts: ResourceOptions = None
    ):
        super().__init__("kubernetes:index:Cluster", name, {}, opts)

        def id_to_dict(id_output) -> Mapping[str, Any]:
            my_dict = {}
            my_dict[id_output] = {}
            return my_dict

        cluster_identity = managedidentity.UserAssignedIdentity(
            f"{name}-useridentity",
            resource_group_name=args.resource_group_name,
            opts=ResourceOptions(parent=self),
        )

        subnet_role_assignment = authorization.RoleAssignment(
            f"{name}-roleassignment",
            principal_id=cluster_identity.principal_id,
            principal_type="ServicePrincipal",
            scope=args.subnet_id,
            role_definition_id=Output.concat(
                "/subscriptions/",
                args.subscription_id,
                "/providers/Microsoft.Authorization/roleDefinitions/4d97b98b-1d4f-4787-a291-c67834d212e7",
            ),
            opts=ResourceOptions(parent=self),
        )

        self.cluster = containerservice.ManagedCluster(
            f"{name}-cluster",
            resource_group_name=args.resource_group_name,
            agent_pool_profiles=[
                containerservice.ManagedClusterAgentPoolProfileArgs(
                    count=args.node_count,
                    max_pods=50,
                    mode="System",
                    os_disk_size_gb=30,
                    os_type="Linux",
                    type="VirtualMachineScaleSets",
                    vm_size="Standard_DS3_v2",
                    vnet_subnet_id=args.subnet_id,
                    name="nodepool",
                )
            ],
            dns_prefix=args.resource_group_name,
            enable_rbac=True,
            kubernetes_version=args.kubernetes_version,
            identity=containerservice.ManagedClusterIdentityArgs(
                type="UserAssigned",
                user_assigned_identities=cluster_identity.id.apply(id_to_dict),
            ),
            service_principal_profile=containerservice.ManagedClusterServicePrincipalProfileArgs(
                client_id="msi"
            ),
            opts=ResourceOptions(parent=self),
        )

        credentials = containerservice.list_managed_cluster_admin_credentials_output(
            resource_group_name=args.resource_group_name,
            resource_name=self.cluster.name,
        )

        kubeconfig = credentials.kubeconfigs[0].value.apply(
            lambda enc: base64.b64decode(enc).decode()
        )

        self.kube_config = kubeconfig

        self.k8sProvider = Provider(
            "k8s_provider", kubeconfig=kubeconfig, opts=ResourceOptions(parent=self)
        )

        self.register_outputs(
            {"k8sProvider": self.k8sProvider, "cluster": self.cluster,
                "kube_config": self.kube_config}
        )
