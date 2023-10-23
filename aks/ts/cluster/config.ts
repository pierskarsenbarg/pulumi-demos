import { StackReference, getStack, Config} from "@pulumi/pulumi";

import {getValue} from "../common/output";

export const getConfig = async () => {
    const stackName = getStack();
    const baseStackReferenceUrl: string = `pierskarsenbarg/monorepo-k8s-base-ts/${stackName}`;
    const baseStack = new StackReference(baseStackReferenceUrl);

    const resourceGroupNameValue = await baseStack.getOutputDetails("resourceGroupName");
    const resourceGroupName = getValue<string>(resourceGroupNameValue, "");

    const networkStackReferenceUrl: string = `pierskarsenbarg/monorepo-k8s-network-ts/${stackName}`;
    const networkStack = new StackReference(networkStackReferenceUrl)
    
    const vnetIdValue = await networkStack.getOutputDetails("vnetId")
    const subnetIdValue = await networkStack.getOutputDetails("subnetId")

    const vnetId = getValue<string>(vnetIdValue, "");
    const subnetId = getValue<string>(subnetIdValue, "");

    const stackConfig = new Config();
    const subscriptionId = stackConfig.requireSecret("subscriptionId");

    return {
        resourceGroupName,
        vnetId,
        subnetId,
        subscriptionId
    };
}
