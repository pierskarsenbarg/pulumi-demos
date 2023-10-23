import * as resources from "@pulumi/azure-native/resources";

const resourceGroup = new resources.ResourceGroup("aks-typescript");

export const resourceGroupName = resourceGroup.name;
