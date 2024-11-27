variable ECR_NAME {
    type = string
    description = "Holds the ECR Name."
}

variable IMAGE_NAME {
    type = string
    description = "Holds the Image Name of the ETL image in the ECR."
}

variable ECS_CLUSTER_NAME {
    type = string
    description = " Holds the ECS Cluster name "
}

variable VPC_ID {
    type = string
    description = " Holds VPC ID "
}

variable SECURITY_GROUP_ID {
    type = string
    description = " Holds Security Group ID from the VPC "
}

variable PUBLIC_TAG {
    type = string
    description = " The Public tag in front of a Public Subnet"
}