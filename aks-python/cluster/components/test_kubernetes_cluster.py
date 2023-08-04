from email.mime import base
import pulumi
import base64

kubeconfig = base64.b64encode(bytes("foo", "utf-8"))


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        outputs = args.inputs
        if args.typ == "azure-native:containerservice:ManagedCluster":
            outputs = {
                **args.inputs,
            }
        return [args.name + "_id", outputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        if (
            args.token
            == "azure-native:containerservice:listManagedClusterAdminCredentials"
        ):
            return {
                "kubeconfigs": [
                    {
                        "name": "foo",
                        "value": kubeconfig.decode("ascii"),
                    }
                ]
            }
        return {}


pulumi.runtime.set_mocks(MyMocks())


import kubernetes_cluster

cluster = kubernetes_cluster.KubernetesCluster(
    "foo",
    args=kubernetes_cluster.KubernetesClusterArgs(
        kubernetes_version="1.18",
        node_count=3,
        resource_group_name="foo",
        vnet_id="foo",
        subnet_id="foo",
        subscription_id="foo",
    ),
)


@pulumi.runtime.test
def test_version():
    def check_version(version):
        assert version == "1.18"

    return cluster.cluster.kubernetes_version.apply(check_version)
