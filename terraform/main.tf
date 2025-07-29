# Grab the most recent Amazon Linux 2 AMI.

data "aws_ami" "this" {
    most_recent = true
    owners = ["amazon"]

    filter {
        name = "name"
        values = ["al2023-ami-20*"]
    }

    filter {
        name = "architecture"
        values = ["x86_64"]
        #values = ["arm64"]
    }
}

#uh, pick one of the three private subnets at random so we don't fill the first one.
resource "random_integer" "subnet" {
    min = 0
    max = 2
}

resource "random_id" "this" {
    byte_length = 8
}

resource "aws_security_group" "this" {
    name = "${var.app_name}-${random_id.this.id}"
    description = "Security group helper from n2-sandbox-helpers"
    vpc_id = module.core_info.vpc_id

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["10.0.0.0/8"]
    }
    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["10.0.0.0/8"]
    }
    ingress {
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = ["10.0.0.0/8"]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}


#The actual instance
resource "aws_instance" "this" {
    ami = data.aws_ami.this.id
    instance_type = var.instance_type

    subnet_id = module.core_info.private_subnets[random_integer.subnet.result]
    vpc_security_group_ids = [ aws_security_group.this.id ]
    iam_instance_profile = aws_iam_instance_profile.this.name
    tags = {
        "Name" = "${var.app_name}-${random_id.this.id}"
    }
}


# Moving all the spammy IAM role stuff here. We are just setting up an IAM instance role to allow SSM Connect and patch manager to function.
resource "aws_iam_instance_profile" "this" {
    name = "${var.app_name}-${random_id.this.id}"
    role = aws_iam_role.this.name
}

resource "aws_iam_role" "this" {
    name = "${var.app_name}-${random_id.this.id}"
    path = "/"
    assume_role_policy = data.aws_iam_policy_document.sts.json
}

data "aws_iam_policy_document" "sts" {
    statement {
        effect = "Allow"

        principals {
          type = "Service"
          identifiers = ["ec2.amazonaws.com"]
        }

        actions = ["sts:AssumeRole"]
    }
}

data "aws_iam_policy" "ssm" {
    arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ssm" {
    role = aws_iam_role.this.name
    policy_arn = data.aws_iam_policy.ssm.arn
}


# Grab us some core-info. Not versioned in this case because uh, this is sandbox. Don't try this at home, kids.
module "core_info" {
  source              = "git@github.com:Chewy-Inc/core-info-aws-tf-module.git//terraform"
#  source              = "git::https://github.com/Chewy-Inc/core-info-aws-tf-module.git//terraform"
  app_name            = var.app_name
  cost_center         = var.cost_center
  data_classification = var.data_classification
  environment         = var.environment
  owner_email         = var.owner_email
  region              = var.region
  segmented_account_name = "worker_sc_fp"
}

# Provider setup. You will probably never need to touch this.
terraform {
  required_version = ">=1.0.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
        "chewy:app_name" = var.app_name
        "chewy:cost_center" = var.cost_center
        "chewy:owner_email" = var.owner_email
        "chewy:environment" = var.environment
        "chewy:created_by" = "n2-sandbox-helpers"
        "chewy:data_classification" = var.data_classification
    }
  }
}

#For people who need the AZ of this instance for reasons
data "aws_network_interface" "this" {
    id = aws_instance.this.primary_network_interface_id
}





# LOAD BALANCER
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name = "${var.app_name}-alb"

  load_balancer_type = "application"
  internal           = false

  vpc_id                = module.core_info.vpc_id
  subnets               = module.core_info.public_subnets
  create_security_group = false
  security_groups       = [aws_security_group.alb_sg.id]

  route53_records = {
    Com = {
      name    = "${var.app_name}-${var.environment}-${module.core_info.short_region}"
      type    = "A"
      zone_id = module.core_info.internal_zone_id
    }
  }
}

# TARGET GROUP
resource "aws_alb_target_group" "lambda_target_group" {
  name        = "apll-ingestion-target-group"
  port = 8000
  protocol = "HTTP"
  vpc_id = module.core_info.vpc_id
}

resource "aws_lb_target_group_attachment" "apll_lambda" {
  target_group_arn = aws_alb_target_group.lambda_target_group.arn
  target_id        = aws_instance.this.id
}

# LISTENER
resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = module.alb.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.lambda_target_group.arn
  }
}

# SECURITY GROUP
resource "aws_security_group" "alb_sg" {
  name        = "apll-ingestion-alb-sg"
  description = "Allow inbound POST requests from specific IP"
  vpc_id      = module.core_info.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "chewyips" {
  for_each = toset(compact(concat(module.core_info.chewy_private_cidrs, module.core_info.chewy_public_cidrs)))

  security_group_id = aws_security_group.alb_sg.id
  cidr_ipv4         = each.value
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}


resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = -1
  to_port           = -1
  ip_protocol       = "-1"
}

data "aws_acm_certificate" "cert" {
  domain = "*.${module.core_info.internal_zone_name}"
}