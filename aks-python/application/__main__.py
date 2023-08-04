from pulumi import ResourceOptions
from pulumi_kubernetes import Provider
from config import ApplicationConfig
from components.application import Application, ApplicationArgs

application_config = ApplicationConfig()

k8s_provider = Provider("provider", kubeconfig=application_config.kube_config)

application = Application(
    "kuad",
    ApplicationArgs(
        replicas=1,
        application_name="kuad",
        image_uri=application_config.application_image,
        container_port=8080,
        hostname=application_config.hostname,
    ),
    opts=ResourceOptions(provider=k8s_provider),
)
