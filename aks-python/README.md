# Pulumi AKS Reference

This repo serves as a reference architecture for an Azure Kubernetes Service cluster, following several best practices recommended by the Pulumi SE team.

## Project Separation

Pulumi recommends separating your Pulumi projects into separate directories, either as part of a mono-repo or distinct Git repositories.

The primary reason for this is to ensure a reduction in the blast radius for parts of your infrastructure, as well as considering the rate of change of your infrastructure.

In order to reference between projects, stack references have been employed to link outputs from projects as inputs to other projects.

### Rate of Change

Rate of change is a consideration for how often your infrastructure at this layer will change once declared.

Networking components will change rarely, Kubernetes clusters will change more often, but still on a rare occasion. Applications change regularly as part of a continuous deployment methodology.

Separating these parts of your infrastructure means the rate of change will not affect components outside the scope of your blast radius.

## Use of Components

Parts of your infrastructure stack will be reused across teams, and infrastructure. The team has implemented several components in order to show how these work.

These components are:

- A kubernetes cluster component, to create a best practice AKS cluster
- A managed Kubernetes component, which includes common services to make a cluster usable, like an ingress controller
- An application component, to simplify the reuse of application deployments

These components are designed with inputs and outputs for reusability.

## Policy

A policy pack has been created to show how policy can be used to set guard rails around infrastructure. This policy can be tested and used locally using the cli, or published to the Pulumi service and set organization wide to ensure compliance of infrastructure.