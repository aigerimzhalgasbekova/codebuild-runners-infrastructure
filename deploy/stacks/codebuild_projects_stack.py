"""Stack for creating AWS CodeBuild projects.

This module contains the AWS CDK stack that creates the CodeBuild projects
for GitHub Actions runners based on the provided configuration.
"""

from typing import Any

from aws_cdk import Stack
from constructs import Construct

from ..constructs.codebuild_project import CodeBuildProject
from ..lib.codebuild_dataclasses import EnvConfig
from .synthesizer import StackSynthesizer


class CodeBuildProjectStack(Stack):
    """Stack that creates CodeBuild projects for GitHub Actions runners.

    This stack creates one or more CodeBuild projects based on the provided
    configuration. Each project is set up with VPC integration, GitHub webhooks,
    and appropriate IAM roles.

    Attributes:
        None
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_config: EnvConfig,
        **kwargs: Any,
    ) -> None:
        """Initialize the CodeBuild projects stack.

        Args:
            scope: The scope in which to define this stack
            construct_id: The scoped construct ID
            env_config: Configuration for the environment and projects
            **kwargs: Additional arguments to pass to the parent stack
        """
        super().__init__(
            scope,
            construct_id,
            synthesizer=StackSynthesizer(env_config.qualifier),
            **kwargs,
        )

        for project_spec in env_config.codebuild_projects:
            CodeBuildProject(
                self,
                f"{project_spec.owner}-{project_spec.repository}",
                project_spec=project_spec,
            )
