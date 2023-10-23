import { StackReference, getStack, Config} from "@pulumi/pulumi";

import {getValue} from "../common/output";

export const getConfig = async () => {
    const stackName = getStack();
    const clusterStack = new StackReference(`pierskarsenbarg/monorepo-k8s-cluster-ts/${stackName}`);
    const kubeConfigDetails = await clusterStack.getOutputDetails("kubeConfig");
    const kubeConfigValue = await getValue<string>(kubeConfigDetails, "");

    const stackConfig = new Config();
    const hostName = stackConfig.require("hostname");
    const applicationImage = stackConfig.require("applicationimage");

    return {
        kubeConfigValue,
        hostName,
        applicationImage
    };
}