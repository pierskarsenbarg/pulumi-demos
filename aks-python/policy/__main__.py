from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)

import pulumi

supported_kubernetes_versions = ["1.27", "1.26"]


def kubernetes_version_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if args.resource_type == "azure-native:containerservice:ManagedCluster" and "kubernetesVersion" in args.props:
        kubernetes_version = args.props["kubernetesVersion"]
        if kubernetes_version is not None and kubernetes_version[0:3] not in supported_kubernetes_versions:
            report_violation(
                "This version of Kubernetes is not supported. Please use one of the approved versions only")


valid_kubernetes_version = ResourceValidationPolicy(
    name="valid-kubernetes-version",
    description="Prohibits the use of unsupported Kubernetes versions",
    validate=kubernetes_version_validator,
)

PolicyPack(
    name="azure-python",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        valid_kubernetes_version,
    ],
)
