import { Config, StackReference, getStack} from "@pulumi/pulumi";

import {getValue} from "../common/output";

export const getConfig = async () => {
    const stackName = getStack();
    const baseStackReferenceUrl: string = `pierskarsenbarg/monorepo-k8s-base-ts/${stackName}`;
    const baseStack = new StackReference(baseStackReferenceUrl);

    const resourceGroupNameValue = await baseStack.getOutputDetails("resourceGroupName");
    const resourceGroupName = getValue<string>(resourceGroupNameValue, "");
    
    const stackConfig = new Config();
    const vnetCidr = stackConfig.require("vnetcidr");
    const subnetCidr = stackConfig.require("subnetcidr");

    return {
        resourceGroupName,
        vnetCidr,
        subnetCidr
    };
}

