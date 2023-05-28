# Deployments for Kafka in kraft mode

There are two types of deployments in this folder:

- deploy.yaml: In the cluster, a Kafka node is either a controller or a broker. 
- mix-deploy.yaml: In the cluster, some Kafka nodes are both controllers and brokers. The other nodes are brokers only. To unify the deployment, we use the same tfvars where the so-called 'controller' hosts are actually playing two roles.