variable TRANSFER_DATA_ECR_NAME {
    type = string
    description = "ECR Name for Long term storage transfer"
}


variable ETL_ECR_NAME {
    type = string
    description = "ECR name for ETL process"
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