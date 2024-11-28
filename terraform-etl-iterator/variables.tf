variable ECR_NAME {
    type = string
    description = "Holds the ECR Name."
}


variable ECS_CLUSTER_NAME {
    type = string
    description = " Holds the ECS Cluster name "
}

variable VPC_ID {
    type = string
    description = " Holds VPC ID "
}

variable SUBNET_IDS {
    type = list(string)
    description = " List of Public Subnet IDs "
}