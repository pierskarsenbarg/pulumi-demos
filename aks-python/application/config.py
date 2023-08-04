from pulumi import Config, StackReference, get_stack, Output


class ApplicationConfig():
    application_image: Output[str]
    hostname: Output[str]
    kube_config: Output[str]
    replicas: Output[int]

    def __init__(self):
        stack_name = get_stack()

        config = Config()

        self.application_image = config.require("applicationimage")
        self.hostname = config.require("hostname")
        self.replicas = 1 if config.get("replicas") == 0 else config.get("replicas")

        org_name = config.require("orgname")

        cluster_stackreference = StackReference(
            f"{org_name}/monorepo-k8s-cluster/{stack_name}")
        self.kube_config = cluster_stackreference.require_output("kube_config")
