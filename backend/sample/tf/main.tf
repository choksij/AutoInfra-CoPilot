resource "aws_s3_bucket" "logs" {
  bucket = "copilot-demo-logs"
  acl    = "public-read"         # public ACL

  # missing:
  # block_public_acls = true
  # versioning { enabled = true }
}

resource "aws_security_group" "ssh_all" {
  name        = "ssh-open"
  description = "allows ssh from anywhere"

  ingress {
    from_port   = 22              # sensitive port
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # open to the world
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "db" {
  identifier           = "copilot-db"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "admin"
  password             = "example-pass-123"
  publicly_accessible  = true     # should be false
}
