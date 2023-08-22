from pulumi_azure_native import storage
from pulumi_azure_native import resources

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("resource_group")

# Create an Azure resource (Storage Account)
account = storage.StorageAccount(
    "sa",
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2,
)


blob_container = storage.BlobContainer("blobcontainer",
                                    resource_group_name=resource_group.name,
                                    account_name=account.name,
                                    public_access=storage.PublicAccess.NONE
                                       )