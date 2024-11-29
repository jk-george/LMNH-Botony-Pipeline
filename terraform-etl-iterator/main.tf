provider "aws" {
  region = "eu-west-2" 
}

data "aws_vpc" "VPC" {
  id = var.VPC_ID
}

data "aws_ecr_repository" "ETL-ecr-repo" {
    name = var.ETL_ECR_NAME
}

data "aws_ecr_repository" "transfer-ecr-repo" {
    name = var.TRANSFER_DATA_ECR_NAME
}


data "aws_ecs_cluster" "ecs_cluster" {
  cluster_name = var.ECS_CLUSTER_NAME
}

resource "aws_iam_role" "ecs_role" {
  name               = "connect4-ETL-task-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = ""
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect    = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_readonly" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ecs_full_access" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access" {
  role       = aws_iam_role.ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}





resource "aws_iam_role" "scheduler_ecs_role" {
  name = "connect4-scheduler-ETL-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "scheduler.amazonaws.com" 
        }
        Effect = "Allow"
      }
    ]
  })
}



resource "aws_iam_policy" "scheduler_run_task_policy" {
  name        = "connect4-scheduler-run-task-policy"
  description = "Allows ECS tasks to be run and pass roles"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "attach_ecs_run_task_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = aws_iam_policy.scheduler_run_task_policy.arn
}



resource "aws_iam_role_policy_attachment" "scheduler_ecs_role_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"  
}



resource "aws_iam_role_policy_attachment" "scheduler_logs_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess" 
}

resource "aws_iam_role_policy_attachment" "scheduler_container_registry_readonly" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "scheduler_vpc_access" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
}






# Task for running the ETL
resource "aws_ecs_task_definition" "etl-task-def" {
  family                   = "connect4-ETL-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_role.arn
  task_role_arn            = aws_iam_role.ecs_role.arn
  container_definitions    = jsonencode([
    {
      name      = var.TRANSFER_DATA_ECR_NAME
      image     = format("%s:latest", data.aws_ecr_repository.transfer-ecr-repo.repository_url )
      essential = true
      cpu       = 256
      memory    = 512
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        },
        {
          containerPort = 443
          hostPort      = 443
        }

      ]
      environment = [
        {
          name  = "ENV_VAR_NAME"
          value = "some_value"
        },
        {
          name  = "ANOTHER_ENV_VAR"
          value = "another_value"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/connect4-ETL-task"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

# Task that will run the long term storage data transfer.
resource "aws_ecs_task_definition" "transfer-task-def" {
  family                   = "connect4-transfer-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_role.arn
  task_role_arn            = aws_iam_role.ecs_role.arn
  container_definitions    = jsonencode([
    {
      name      = var.ETL_ECR_NAME
      image     = format("%s:latest", data.aws_ecr_repository.etl-ecr-repo.repository_url )
      essential = true
      cpu       = 256
      memory    = 512
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        },
        {
          containerPort = 443
          hostPort      = 443
        }

      ]
      environment = [
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_USER"
          value = var.DB_USER
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASSWORD
        },
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        },
        {
          name  = "BUCKET"
          value = var.BUCKET
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/connect4-transfer-task"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}



resource "aws_scheduler_schedule_group" "connect4-schedule-group" {
  name = "connect4-schedule-group"
}

resource "aws_security_group" "task_exec_security_group"{
  name        = "connect4-sg-etl-task"
  description = "Allow inbound HTTPS traffic on port 443 from anywhere"
  vpc_id      = var.VPC_ID  

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
    ipv6_cidr_blocks = ["::/0"]
  }
  ingress {
    from_port   = var.DB_PORT
    to_port     = var.DB_PORT
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port   = var.DB_PORT
    to_port     = var.DB_PORT
    protocol    = "-1"  
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Scheduler for ETL script
resource "aws_scheduler_schedule" "connect4-ETL-scheduler" {
  name       = "connect4-ETL-scheduler"
  group_name = aws_scheduler_schedule_group.connect4-schedule-group.id

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* * ? * * *)"

  target {
    arn      = data.aws_ecs_cluster.ecs_cluster.arn
    role_arn = aws_iam_role.scheduler_ecs_role.arn


    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.etl-task-def.arn
      task_count = 1
      launch_type = "FARGATE"
      group = "connect4-ETL-task"

      network_configuration {
      
        assign_public_ip    = true
        subnets             = var.SUBNET_IDS
        security_groups     = [aws_security_group.task_exec_security_group.id]
      }
    }


  }
}

# Scheduler for Long term data transfer
resource "aws_scheduler_schedule" "connect4-ETL-scheduler" {
  name       = "connect4-ETL-scheduler"
  group_name = aws_scheduler_schedule_group.connect4-schedule-group.id

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 ? * * *)"

  target {
    arn      = data.aws_ecs_cluster.ecs_cluster.arn
    role_arn = aws_iam_role.scheduler_ecs_role.arn


    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.transfer-task-def.arn
      task_count = 1
      launch_type = "FARGATE"
      group = "connect4-transfer-task"

      network_configuration {
      
        assign_public_ip    = true
        subnets             = var.SUBNET_IDS
        security_groups     = [aws_security_group.task_exec_security_group.id]
      }
    }


  }
}