provider "aws" {
  region = "eu-west-2"  # Specify the AWS region (modify as needed)
}

data "aws_vpc" "VPC" {
  id = var.VPC_ID
}

data "aws_ecr_repository" "ETL-ecr-repo" {
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
          Service = "scheduler.amazonaws.com"  # The service assuming the role
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


# Attach the necessary policies to the IAM role
resource "aws_iam_role_policy_attachment" "scheduler_ecs_role_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"  # Policy for ECS permissions
}


# Attach the CloudWatch Logs policy if your ECS tasks are writing logs
resource "aws_iam_role_policy_attachment" "scheduler_logs_policy" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"  # To write logs to CloudWatch Logs
}

resource "aws_iam_role_policy_attachment" "scheduler_container_registry_readonly" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "scheduler_vpc_access" {
  role       = aws_iam_role.scheduler_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
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
      name      = var.ECR_NAME
      image     = format("%s:latest", data.aws_ecr_repository.ETL-ecr-repo.repository_url )
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



resource "aws_scheduler_schedule_group" "connect4-schedule-group" {
  name = "connect4-schedule-group"
}

resource "aws_security_group" "task_exec_security_group"{
  name        = "connect4-sg-etl-task"
  description = "Allow inbound HTTPS traffic on port 443 from anywhere"
  vpc_id      = var.VPC_ID  # Make sure to replace with your actual VPC ID

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allows inbound HTTPS traffic from any IP
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
  }
}

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