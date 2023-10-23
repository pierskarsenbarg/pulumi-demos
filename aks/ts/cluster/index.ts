import {getConfig} from "./config";
import {ManagedKubernetesCluster} from "./components/managedKubernetesCluster"
import * as pulumi from "@pulumi/pulumi";

export = async () => {
    const config = await getConfig();

    const cluster = new ManagedKubernetesCluster("cluster", {
        kubernetesVersion: "1.28.0",
        nodeCount: 3,
        resourceGroupName: config.resourceGroupName,
        subnetId: config.subnetId,
        vnetId: config.vnetId,
        subscriptionId: config.subscriptionId,
    })

    return {
        kubeConfig: pulumi.secret(cluster.kubeConfig),
        ingressIpAddress: cluster.ingressIpAddress
    };
};