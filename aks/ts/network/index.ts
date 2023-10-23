import * as pulumi from "@pulumi/pulumi";
import * as network from "@pulumi/azure-native/network";
import {getConfig} from "./config";

export = async () => {
    const config = await getConfig();

    const vnet = new network.VirtualNetwork("aks-ts-vnet", {
        addressSpace: {
            addressPrefixes: [config.vnetCidr]
        },
        resourceGroupName: config.resourceGroupName
    }, {
        ignoreChanges: ["subnets", "etags"]
    });

    const subnet = new network.Subnet("aks-ts-subnet", {
        virtualNetworkName: vnet.name,
        resourceGroupName: config.resourceGroupName,
        addressPrefix: config.subnetCidr
    });

    return {
        vnetId: vnet.id,
        subnetId: subnet.id,
    };
}

