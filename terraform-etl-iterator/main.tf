provider "aws" {
  region = "eu-west-2"  # Specify the AWS region (modify as needed)
}

data "aws_vpc" "VPC" {
  id = var.VPC_ID
}

data "aws_subnets" "SUBNETS_IN_VPC" {
  filter {
    name = "vpc-id"
    values = [var.VPC_ID]
  }
}

data "aws_security_group" "selected" {
  id = var.SECURITY_GROUP_ID
}

data "aws_ecr_repository" "ETL-ecr" {
    name = var.ECR_NAME
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
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "ecs.amazonaws.com"
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
      name      = "connect4-etl-task-container"
      image     = var.IMAGE_NAME
      essential = true
      cpu       = 256
      memory    = 512
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
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
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}







resource "aws_scheduler_schedule" "connect4-ETL-scheduler" {
  name       = "connect4-ETL-scheduler"
  group_name = "connect4-schedule-group"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* * ? * * *)"

  target {
    arn      = aws_ecs_cluster.ecs_cluster.arn
    role_arn = aws_iam_role.ecs_role.arn


    ecs_parameters {
        task_definition_arn = aws_ecs_task_definition.etl-task-def.arn
        task_count = 1
        launch_type = "FARGATE"

        network_configuration {
          subnets             = aws_subnets.SUBNETS_IN_VPC.ids
        }

    }


  }
}