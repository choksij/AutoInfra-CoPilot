from __future__ import annotations

import re
from pathlib import Path
from typing import List

from ..models import Finding


# Simple regex-based rules for speed and demo clarity
CIDR_OPEN_RE = re.compile(r'0\.0\.0\.0/0')
PORT_RE = re.compile(r'(\bfrom_port\b|\bto_port\b)\s*=\s*(\d+)')
S3_ACL_PUBLIC_RE = re.compile(r'acl\s*=\s*"(public-read|public-read-write)"')
S3_BLOCK_PUBLIC_ACLS_RE = re.compile(r'block_public_acls\s*=\s*true')
S3_VERSIONING_ENABLED_RE = re.compile(r'versioning\s*{[^}]*enabled\s*=\s*true', re.DOTALL)
RDS_PUBLIC_RE = re.compile(r'publicly_accessible\s*=\s*true')


SENSITIVE_PORTS = {"22", "3389", "80", "443"}


def _scan_file(path: Path) -> List[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    findings: List[Finding] = []

    # POLICY_001: No 0.0.0.0/0 on sensitive ports in security groups
    if CIDR_OPEN_RE.search(text):
        # try to locate an offending port near the open CIDR
        ports = set(m.group(2) for m in PORT_RE.finditer(text))
        if ports & SENSITIVE_PORTS:
            # best-effort line number for the CIDR occurrence
            line = text[: text.find("0.0.0.0/0")].count("\n") + 1
            findings.append(
                Finding(
                    tool="policy",
                    rule_id="POLICY_001",
                    severity="CRITICAL",
                    file=str(path.name),
                    line=line,
                    message="Security Group allows 0.0.0.0/0 on a sensitive port (22/3389/80/443).",
                )
            )

    # POLICY_002: S3 buckets must not be public and must enable versioning + block_public_acls
    if S3_ACL_PUBLIC_RE.search(text):
        line = text[: S3_ACL_PUBLIC_RE.search(text).start()].count("\n") + 1
        findings.append(
            Finding(
                tool="policy",
                rule_id="POLICY_002",
                severity="HIGH",
                file=str(path.name),
                line=line,
                message='S3 bucket has public ACL (acl="public-read" or similar).',
            )
        )
    # missing block_public_acls or versioning enabled
    if "resource \"aws_s3_bucket\"" in text:
        if not S3_BLOCK_PUBLIC_ACLS_RE.search(text):
            line = text.find("resource \"aws_s3_bucket\"")
            line_no = text[: line].count("\n") + 1 if line >= 0 else 1
            findings.append(
                Finding(
                    tool="policy",
                    rule_id="POLICY_002",
                    severity="HIGH",
                    file=str(path.name),
                    line=line_no,
                    message="S3 bucket missing `block_public_acls = true`.",
                )
            )
        if not S3_VERSIONING_ENABLED_RE.search(text):
            line = text.find("resource \"aws_s3_bucket\"")
            line_no = text[: line].count("\n") + 1 if line >= 0 else 1
            findings.append(
                Finding(
                    tool="policy",
                    rule_id="POLICY_002",
                    severity="HIGH",
                    file=str(path.name),
                    line=line_no,
                    message="S3 bucket missing `versioning { enabled = true }`.",
                )
            )

    # POLICY_003: RDS must not be publicly accessible
    if RDS_PUBLIC_RE.search(text):
        line = text[: RDS_PUBLIC_RE.search(text).start()].count("\n") + 1
        findings.append(
            Finding(
                tool="policy",
                rule_id="POLICY_003",
                severity="HIGH",
                file=str(path.name),
                line=line,
                message="RDS instance has `publicly_accessible = true`.",
            )
        )

    return findings


def run_policy_checks(base_dir: str) -> List[Finding]:
    findings: List[Finding] = []
    for p in Path(base_dir).rglob("*.tf"):
        findings.extend(_scan_file(p))
    return findings
