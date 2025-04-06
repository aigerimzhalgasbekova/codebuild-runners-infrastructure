#!/usr/bin/env python3
"""Main entry point for the CodeBuild runners infrastructure.

This script creates and deploys the CodeBuild infrastructure for GitHub Actions runners.
It sets up CodeBuild projects with VPC integration, GitHub webhooks, and appropriate
IAM roles for each configured repository.
"""

from aws_cdk import App, Environment

from deploy.config import env_config
from deploy.stacks.codebuild_projects_stack import CodeBuildProjectStack


def main() -> None:
    """Create and deploy the CodeBuild infrastructure."""
    app = App()

    print("Creating codebuild projects...")
    CodeBuildProjectStack(
        app,
        "codebuild-projects",
        env_config,
        env=Environment(
            account=env_config.aws_account_id, region=env_config.aws_region
        ),
    )
    print("Created codebuild-projects stack")

    app.synth()


if __name__ == "__main__":
    main()
