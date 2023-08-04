from pulumi import ResourceOptions, export
from pulumi_azure_native import network
from config import NetworkConfig

network_config = NetworkConfig()

vnet = network.VirtualNetwork(
    "aks-vnet",
    address_space=network.AddressSpaceArgs(
        address_prefixes=[network_config.vnet_cidr]),
    resource_group_name=network_config.resource_group_name,
    opts=ResourceOptions(ignore_changes=["subnets", "etags"]),
)

subnet = network.Subnet(
    "aks-subnet",
    virtual_network_name=vnet.name,
    resource_group_name=network_config.resource_group_name,
    address_prefix=network_config.subnet_cidr,
)

export("vnetid", vnet.id)
export("subnetid", subnet.id)
