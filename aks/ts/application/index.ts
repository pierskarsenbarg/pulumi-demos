import {Application} from "./components/application";
import { getConfig } from "./config";
import {Provider} from "@pulumi/kubernetes";


export = async() => {
    const appConfig = await getConfig();

    const k8sProvider = new Provider("provider", {
        kubeconfig: appConfig.kubeConfigValue
    });

    const application = new Application("kuad", {
        replicas: 1,
        applicationName: "kuad",
        imageUri: appConfig.applicationImage,
        containerPort: 8080,
        hostname: appConfig.hostName
    }, {provider: k8sProvider})
}

