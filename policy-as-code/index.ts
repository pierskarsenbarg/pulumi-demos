import * as aws from "@pulumi/aws";
import { PolicyPack, validateResourceOfType, ResourceValidationPolicy } from "@pulumi/policy";

const supportedVersions: string[] = ["1.26", "1.27", "1.25"];

const k8sVersionPolicy: ResourceValidationPolicy = {
    name: "kubernetes-version",
    description: "Ensure that the kubernetes version is compliant",
    enforcementLevel: "mandatory",
    validateResource: validateResourceOfType(aws.eks.Cluster, (cluster, args, reportViolation) => {
        if(cluster.version !== undefined &&
            cluster.version.length > 4 && 
            supportedVersions.indexOf(cluster.version.substring(0, 3)) === -1) {
            reportViolation(
                "Kubernetes API version must be either 1.27 or 1.26 or 1.25"
            )
        }
    })
}

new PolicyPack("piers-aws-eks-demo", {
    policies: [k8sVersionPolicy],
});
