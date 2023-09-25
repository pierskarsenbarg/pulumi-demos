import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";


const stackref = new pulumi.StackReference("pierskarsenbarg/stack-reference-network/dev");

const vpcid = stackref.getOutput("vpcid");

const securitygroup = new aws.ec2.SecurityGroup("secgroup", {
    vpcId: vpcid,
    ingress: [{
        cidrBlocks: ["0.0.0.0/0"],
        protocol: "tcp",
        toPort: 80,
        fromPort: 80
    }]
})