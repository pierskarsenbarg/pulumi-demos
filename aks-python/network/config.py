from pulumi import Config, StackReference, get_stack, Output


class NetworkConfig():
    vnet_cidr: Output[str]
    subnet_cidr: Output[str]
    resource_group_name: Output[str]

    def __init__(self):
        stack_name = get_stack()

        config = Config()

        self.vnet_cidr = config.require("vnetcidr")
        self.subnet_cidr = config.require("subnetcidr")
        org_name = config.require("orgname")

        base_stackreference_uri = f"{org_name}/monorepo-k8s-base/{stack_name}"
        base_stackreference = StackReference(base_stackreference_uri)

        self.resource_group_name = base_stackreference.require_output(
            "resourceGroupName")
