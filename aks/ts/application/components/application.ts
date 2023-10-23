import {ComponentResource, ResourceOptions, Output} from "@pulumi/pulumi";
import {Namespace, Service} from "@pulumi/kubernetes/core/v1";
import { Deployment } from "@pulumi/kubernetes/apps/v1";
import {Ingress} from "@pulumi/kubernetes/networking/v1";

interface ApplicationArgs {
    replicas: number,
    applicationName: string,
    imageUri: string,
    containerPort: number,
    hostname: string
}

export class Application extends ComponentResource {
    constructor(name: string, args: ApplicationArgs, opts?: ResourceOptions) {
        super("x:index:Application", name, args, opts);

        const portName: string = "http-port";

        if (opts !== undefined) {
            opts.parent = this;
        } else {
            opts = {
                parent: this
            }
        }

        const appNamespace = new Namespace(`${name}-appnamespace`, {}, opts);

        const appLabel = {"app": args.applicationName};

        const appDeployment = new Deployment(`${name}-appdeployment`, {
            metadata: {
                namespace: appNamespace.metadata.name
            },
            spec: {
                replicas: args.replicas,
                selector: {
                    matchLabels: appLabel
                },
                template: {
                    metadata: {labels: appLabel},
                    spec: {
                        containers: [{
                            name: args.applicationName,
                            image: args.imageUri,
                            ports: [{
                                containerPort: args.containerPort,
                                hostPort: 8080
                            }]
                        }]
                    }
                }
            }
        }, opts);

        const appService = new Service(`${name}-appservice`, {
            metadata: {namespace: appNamespace.metadata.name},
            spec: {
                selector: appLabel,
                ports: [{
                    port: 80,
                    targetPort: args.containerPort,
                    name: portName
                }]
            }
        }, opts);

        const appIngress = new Ingress(`${name}-appingress`, {
            metadata: {
                namespace: appNamespace.metadata.name,
                annotations: {
                    "kubernetes.io/ingress.class": "nginx"
                }
            },
            spec: {
                ingressClassName: "nginx",
                rules: [{
                    host: args.hostname,
                    http: {
                        paths: [{
                            pathType: "ImplementationSpecific",
                            path: "/",
                            backend: {
                                service: {
                                    name: appService.metadata.name,
                                    port: {
                                        name: portName
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }, opts)

    }
}