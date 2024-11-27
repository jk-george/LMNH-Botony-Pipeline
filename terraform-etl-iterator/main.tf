provider "aws" {
  region = "eu-west-2"  # Specify the AWS region (modify as needed)
}


data "aws_ecr_repository" "ETL-ecr" {
    name = var.ECR_NAME
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
    }
  ])

  volume {
    name      = "service-storage"
    host_path = "/ecs/service-storage"
  }

  runtime_platform {
    operating_system_family = "WINDOWS_SERVER_2019_CORE"
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
    arn      = aws_sqs_queue.example.arn
    role_arn = aws_iam_role.example.arn
  }
}