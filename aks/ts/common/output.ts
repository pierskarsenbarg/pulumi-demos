import { StackReferenceOutputDetails } from "@pulumi/pulumi";

export function getValue<T>(input: StackReferenceOutputDetails, defaultValue: T): T {
    if (!input) {
        return defaultValue;
    }

    if (input.value) {
        return <T>input.value!;
    }

    if (input.secretValue) {
        return <T>input.secretValue!;
    }

    return defaultValue;
}