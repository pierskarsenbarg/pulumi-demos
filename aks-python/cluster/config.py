from pulumi import Config, StackReference, get_stack, Output


class ClusterConfig():
    subscription_id: Output[str]
    vnet_id: Output[str]
    subnet_id: Output[str]
    resource_group_name: Output[str]

    def __init__(self):
        stack_name = get_stack()

        config = Config()

        self.subscription_id = config.require_secret("subscriptionid")

        org_name = config.require("orgname")

        base_stackreference_uri = f"{org_name}/monorepo-k8s-base/{stack_name}"
        base_stackreference = StackReference(base_stackreference_uri)

        self.resource_group_name = base_stackreference.require_output(
            "resourceGroupName")

        network_stackreference_uri = f"{org_name}/monorepo-k8s-network/{stack_name}"
        network_stackreference = StackReference(network_stackreference_uri)

        self.vnet_id = network_stackreference.require_output("vnetid")
        self.subnet_id = network_stackreference.require_output("subnetid")
