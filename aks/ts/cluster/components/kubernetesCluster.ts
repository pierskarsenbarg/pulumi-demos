import { ComponentResource, ComponentResourceOptions, Output, Input, ResourceOptions, interpolate } from "@pulumi/pulumi";
import * as containerService from "@pulumi/azure-native/containerservice";
import * as managedIdentity from "@pulumi/azure-native/managedidentity";
import * as authorization from "@pulumi/azure-native/authorization";
import {Provider} from "@pulumi/kubernetes";

export interface KubernetesClusterArgs {
    kubernetesVersion: string,
    resourceGroupName: string,
    nodeCount: number, 
    vnetId: string,
    subnetId: string,
    subscriptionId: Output<string>
}

export class KubernetesCluster extends ComponentResource {
    public readonly K8sProvider: Provider;
    public readonly Cluster: containerService.ManagedCluster;
    public readonly KubeConfig: Output<string>;
    constructor(name: string, args: KubernetesClusterArgs, opts?: ResourceOptions) {
        super("x:index:KubernetesCluster", name, args, opts);

        const getId = (id: string) => {
            const dict: {[key: string]: object} = {};
            dict[id] = {};
            return dict; 
        }

        const clusterIdentity = new managedIdentity.UserAssignedIdentity(`${name}-useridentity`, {
           resourceGroupName: args.resourceGroupName
        }, {
            parent: this
        });

        const subnetRoleAssignment = new authorization.RoleAssignment(`${name}-roleassignment`, {
            principalId: clusterIdentity.principalId,
            principalType: "ServicePrincipal",
            scope: args.subnetId,
            roleDefinitionId: interpolate`/subscriptions/${args.subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/4d97b98b-1d4f-4787-a291-c67834d212e7`
        }, {
            parent: this
        });

        this.Cluster = new containerService.ManagedCluster(`${name}-cluster`,{
            resourceGroupName: args.resourceGroupName,
            agentPoolProfiles: [
                {
                    count: args.nodeCount,
                    maxPods: 50,
                    mode: "System",
                    osDiskSizeGB: 30,
                    osType: "Linux",
                    type: "VirtualMachineScaleSets",
                    vmSize: "Standard_DS3_v2",
                    vnetSubnetID: args.subnetId,
                    name: "nodepool"
                }
            ],
            dnsPrefix: args.resourceGroupName,
            enableRBAC: true,
            kubernetesVersion: args.kubernetesVersion,
            identity: {
                type: "UserAssigned",
                userAssignedIdentities: [clusterIdentity.id]
            },
            servicePrincipalProfile: {
                clientId: "msi"
            }

        }, {
            parent: this
        });

        const credentials = containerService.listManagedClusterAdminCredentialsOutput({
            resourceGroupName: args.resourceGroupName,
            resourceName: this.Cluster.name
        });

        this.KubeConfig = credentials.kubeconfigs[0].value.apply(kc => Buffer.from(kc, "base64").toString());
        this.K8sProvider = new Provider(`${name}-k8sProvider`, {
            kubeconfig: this.KubeConfig
        })

        this.registerOutputs({
            "k8sProvider": this.K8sProvider,
            "cluster": this.Cluster,
            "kubeConfig": this.KubeConfig
        })
    }
}