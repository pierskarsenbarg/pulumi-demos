import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const lambdaRole = new aws.iam.Role("simpleLambdaRole", {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal(aws.iam.Principals.LambdaPrincipal),
    managedPolicyArns: [aws.iam.ManagedPolicies.AWSLambdaBasicExecutionRole]
});

const lambda = new aws.lambda.CallbackFunction("simpleApiLambda", {
    callback: async (e) => {
        console.log(e);
        return {
            statusCode: 200,
            body: JSON.stringify({message: "Hello, World!"})
        };
    },
    role: lambdaRole
});

const apigw = new aws.apigatewayv2.Api("httpApi", {
    protocolType: "HTTP",
    routeKey: "GET /",
    target: lambda.invokeArn
});

const permission = new aws.lambda.Permission("permission", {
    action: "lambda:InvokeFunction",
    principal: "apigateway.amazonaws.com",
    function: lambda,
});

export const endpoint = apigw.apiEndpoint;