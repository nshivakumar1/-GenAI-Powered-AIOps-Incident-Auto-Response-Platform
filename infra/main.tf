provider "aws" {
  region = "us-east-1"
}

# --- VPC & Networking (Simplified for Demo) ---
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "aiops-demo-vpc"
  }
}

resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"

  tags = {
    Name = "aiops-public-subnet-a"
  }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1b"

  tags = {
    Name = "aiops-public-subnet-b"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "aiops-igw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "aiops-public-rt"
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}

# --- ECR Repository ---
resource "aws_ecr_repository" "victim_service" {
  name                 = "aiops-victim-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "main" {
  name = "aiops-cluster"
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# --- EventBridge Bus ---
resource "aws_cloudwatch_event_bus" "aiops_bus" {
  name = "aiops-incident-bus"
}

# --- Log Group for Victim Service ---
resource "aws_cloudwatch_log_group" "victim_service" {
  name              = "/ecs/aiops-victim-service"
  retention_in_days = 7
}

# --- Outputs ---
output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnets" {
  value = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
}

output "ecr_repo_url" {
  value = aws_ecr_repository.victim_service.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "event_bus_name" {
  value = aws_cloudwatch_event_bus.aiops_bus.name
}
