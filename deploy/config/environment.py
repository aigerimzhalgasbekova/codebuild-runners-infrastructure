"""Environment configuration for the CodeBuild infrastructure."""

from __future__ import annotations

import os

from ..lib.codebuild_dataclasses import CodeBuildProjectConfig, EnvConfig

# Default values
DEFAULT_AWS_REGION = "eu-west-1"
DEFAULT_AWS_CDK_BOOTSTRAP_QUALIFIER = "hnb659fds"

# Get sensitive values from environment variables with fallbacks to default values
AWS_REGION = os.getenv("AWS_REGION", DEFAULT_AWS_REGION)
AWS_CDK_BOOTSTRAP_QUALIFIER = os.getenv(
    "AWS_CDK_BOOTSTRAP_QUALIFIER", DEFAULT_AWS_CDK_BOOTSTRAP_QUALIFIER
)

# Get AWS account ID with validation
aws_account_id_env = os.getenv("AWS_ACCOUNT_ID")
if not aws_account_id_env:
    error_msg = "AWS_ACCOUNT_ID environment variable must be set"
    raise ValueError(error_msg)
AWS_ACCOUNT_ID: str = aws_account_id_env

# Get GitHub token secret path with validation
github_token_path_env = os.getenv("GITHUB_TOKEN_SECRET_PATH")
if not github_token_path_env:
    error_msg = "GITHUB_TOKEN_SECRET_PATH environment variable must be set"
    raise ValueError(error_msg)
GITHUB_TOKEN_SECRET_PATH: str = github_token_path_env


# Create environment config function
def get_environment_config(project_configs: list[CodeBuildProjectConfig]) -> EnvConfig:
    return EnvConfig(
        aws_account_id=AWS_ACCOUNT_ID,
        aws_region=AWS_REGION,
        codebuild_projects=project_configs,
        qualifier=AWS_CDK_BOOTSTRAP_QUALIFIER,
    )
