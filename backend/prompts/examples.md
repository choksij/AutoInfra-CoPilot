---

```md

### Example Patch: Make S3 bucket private and block public ACLs
```diff
- acl = "public-read"
+ acl = "private"
+ block_public_acls = true

### Example Patch: Make S3 bucket private and block public ACLs
- # versioning not configured
+ versioning {
+   enabled = true
+ }

### Example Patch: Restrict SSH access in Security Group
- cidr_blocks = ["0.0.0.0/0"]
+ cidr_blocks = ["10.0.0.0/24"]  # restrict to trusted CIDR

### Example Patch: Ensure RDS is not publicly accessible
- publicly_accessible = true
+ publicly_accessible = false

### Example Patch: Close open HTTP port (80) on Security Group
- from_port = 80
- to_port   = 80
- cidr_blocks = ["0.0.0.0/0"]
+ # Port 80 disabled; use 443 with restricted CIDR instead
+ from_port = 443
+ to_port   = 443
+ cidr_blocks = ["10.0.0.0/24"]


---

