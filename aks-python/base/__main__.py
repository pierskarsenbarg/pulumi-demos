import pulumi
from pulumi_azure_native import resources

resource_group = resources.ResourceGroup("aks-python")

pulumi.export("resourceGroupName", resource_group.name)
