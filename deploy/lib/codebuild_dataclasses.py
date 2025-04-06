"""Dataclasses for AWS CodeBuild project configuration.

This module provides dataclasses for configuring AWS CodeBuild projects,
including GitHub Actions runners and environment configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aws_cdk import aws_codebuild as codebuild

from .codebuild_environments import AMAZON_LINUX_SMALL


@dataclass
class CodeBuildProjectConfig:
    """Base configuration for a CodeBuild project.

    This class provides the basic configuration options for a CodeBuild project,
    including IAM roles, build environment, and GitHub integration settings.

    Attributes:
        allowed_roles: List of IAM role ARNs that can execute the project.
        build_environment: The build environment configuration.
        gh_token_secret: Path to the GitHub token in AWS Secrets Manager.
        owner: GitHub repository owner.
        repository: GitHub repository name.
    """

    allowed_roles: list[str] = field(default_factory=list)
    build_environment: codebuild.BuildEnvironment = field(
        default_factory=lambda: AMAZON_LINUX_SMALL,
    )
    gh_token_secret: str = ""
    owner: str | None = None
    repository: str | None = None


@dataclass
class GitHubActionsRunner(CodeBuildProjectConfig):
    """Configuration for a GitHub Actions runner using CodeBuild.

    This class extends CodeBuildProjectConfig with required fields for GitHub Actions
    integration. It enforces the presence of GitHub-specific configuration.

    Attributes:
        owner: GitHub repository owner (required).
        repository: GitHub repository name (required).
        gh_token_secret: Path to the GitHub token in AWS Secrets Manager (required).
    """

    # Use fields from the parent class but override with required values
    owner: str = field(default="")  # Will be checked in post_init
    repository: str = field(default="")  # Will be checked in post_init
    gh_token_secret: str = field(default="")  # Will be checked in post_init

    def __post_init__(self) -> None:
        """Validate required fields after initialization.

        Raises:
            TypeError: If any of the required fields are missing.
        """
        if not self.owner or not self.repository or not self.gh_token_secret:
            missing_fields = []
            if not self.owner:
                missing_fields.append("owner")
            if not self.repository:
                missing_fields.append("repository")
            if not self.gh_token_secret:
                missing_fields.append("gh_token_secret")
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            raise TypeError(error_msg)


@dataclass
class EnvConfig:
    """Environment configuration for the CodeBuild infrastructure.

    This class holds the configuration for the entire CodeBuild infrastructure,
    including AWS account details, region, and project configurations.

    Attributes:
        aws_account_id: AWS account ID where resources will be deployed.
        aws_region: AWS region for deployment.
        codebuild_projects: List of CodeBuild project configurations.
        qualifier: CDK bootstrap qualifier for resource naming.
    """

    aws_account_id: str
    aws_region: str
    codebuild_projects: list[CodeBuildProjectConfig]
    qualifier: str
