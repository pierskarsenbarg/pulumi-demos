import {ComponentResource, ResourceOptions, Output, Input, interpolate} from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as components from "./kubernetesCluster";

interface ManagedKubernetesClusterArgs extends components.KubernetesClusterArgs {
   
}

export class ManagedKubernetesCluster extends ComponentResource {
    public readonly ingressIpAddress!: Output<string>;
    public readonly k8sProvider!: k8s.Provider;
    public readonly kubeConfig!: Output<string>;
    constructor(name: string, args: ManagedKubernetesClusterArgs, opts?: ResourceOptions) {
        super("x:index:ManagedCluster", name, args, opts);

        const cluster = new components.KubernetesCluster(`${name}-managedCluster`, {
            kubernetesVersion: args.kubernetesVersion,
            nodeCount: args.nodeCount,
            resourceGroupName: args.resourceGroupName,
            vnetId: args.vnetId,
            subnetId: args.subnetId,
            subscriptionId: args.subscriptionId
        }, {parent: this});

        const nginxIngress = new k8s.helm.v3.Release(`nginxingress`, {
            repositoryOpts: {
                repo: "https://kubernetes.github.io/ingress-nginx"
            },
            chart: "ingress-nginx",
            version: "4.0.16",
            skipAwait: false,
            values: {
                "controller": {
                    "service": {
                        "externalTrafficPolicy": "Local"
                    },
                    "replicaCount": 1,
                    "nodeSelector": {"beta.kubernetes.io/os": "linux"},
                    "admissionWebhooks": {
                        "patch": {"nodeSelector": {"beta.kubernetes.io/os": "linux"}}
                    },
                },
                "defaultBackend": {"nodeSelector": {"beta.kubernetes.io/os": "linux"}},
            }
        }, {parent: this, provider: cluster.K8sProvider});

        const nginxIngressService = k8s.core.v1.Service.get(
            "ingress-svc",
            interpolate`${nginxIngress.status.namespace}/${nginxIngress.status.name}-ingress-nginx-controller`,
            {parent: this, provider: cluster.K8sProvider}
        );

        this.ingressIpAddress = nginxIngressService.status.loadBalancer.ingress[0].ip;
        this.k8sProvider = cluster.K8sProvider;
        this.kubeConfig = cluster.KubeConfig;

        this.registerOutputs({
            "ingressIpAddress": this.ingressIpAddress,
            "k8sProvider": this.k8sProvider,
            "kubeConfig": this.kubeConfig
        });
    }
}