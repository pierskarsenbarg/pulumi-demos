import * as process from "process";
import { RemoteWorkspace, fullyQualifiedStackName } from "@pulumi/pulumi/automation";

const args = process.argv.slice(2);


const org = "pierskarsenbarg";
const project = "simple-api";
const stackName = fullyQualifiedStackName(org, project, "dev");
const awsRegion = "eu-west-1";

(async function() {
    const stack = await RemoteWorkspace.createOrSelectStack({
        stackName,
        url: "https://github.com/pierskarsenbarg/simple-api.git",
        branch: "refs/heads/main",
        projectPath: ".",
    }, {
        envVars: {
            AWS_REGION:            awsRegion,
            AWS_ACCESS_KEY_ID:     process.env.AWS_ACCESS_KEY_ID ?? "",
            AWS_SECRET_ACCESS_KEY: { secret: process.env.AWS_SECRET_ACCESS_KEY ?? "" },
            AWS_SESSION_TOKEN:     { secret: process.env.AWS_SESSION_TOKEN ?? "" },
        },
    });

    const destroy = args.length == 1 && args[0] === "destroy";
    if (destroy) {
        await stack.destroy({ onOutput: console.log });
        console.log("Stack successfully destroyed");
        process.exit(0);
    }

    const upRes = await stack.up({ onOutput: console.log });
    console.log("Update succeeded!");
    console.log(`url: ${upRes.outputs.endpoint.value}`);
})();