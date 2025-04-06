"""Tests for CodeBuild dataclasses."""

import pytest
from aws_cdk import aws_codebuild as codebuild

from deploy.lib.codebuild_dataclasses import (
    CodeBuildProjectConfig,
    EnvConfig,
    GitHubActionsRunner,
)
from deploy.lib.codebuild_environments import (
    AMAZON_LINUX_LARGE,
    AMAZON_LINUX_MEDIUM,
    AMAZON_LINUX_SMALL,
)


def test_codebuild_project_config_defaults() -> None:
    """Test CodeBuildProjectConfig default values."""
    config = CodeBuildProjectConfig()

    assert config.allowed_roles == []
    assert config.build_environment == AMAZON_LINUX_SMALL
    assert config.gh_token_secret == ""
    assert config.owner is None
    assert config.repository is None


def test_github_actions_runner_required_fields() -> None:
    """Test GitHubActionsRunner required fields validation."""
    runner = GitHubActionsRunner(
        owner="test-owner",
        repository="test-repo",
        gh_token_secret="test-secret",
    )

    assert runner.owner == "test-owner"
    assert runner.repository == "test-repo"
    assert runner.gh_token_secret == "test-secret"
    assert isinstance(runner, CodeBuildProjectConfig)


def test_github_actions_runner_missing_fields() -> None:
    """Test GitHubActionsRunner raises error when missing required fields."""
    with pytest.raises(TypeError):
        GitHubActionsRunner(
            owner="test-owner",
            repository="test-repo",
        )


def test_github_actions_runner_with_optional_fields() -> None:
    """Test GitHubActionsRunner with optional fields."""
    runner = GitHubActionsRunner(
        owner="test-owner",
        repository="test-repo",
        gh_token_secret="test-secret",
        allowed_roles=["test-role"],
    )

    assert runner.owner == "test-owner"
    assert runner.repository == "test-repo"
    assert runner.gh_token_secret == "test-secret"
    assert runner.allowed_roles == ["test-role"]


def test_env_config() -> None:
    """Test EnvConfig initialization."""
    config = EnvConfig(
        aws_account_id="123456789012",
        aws_region="us-west-2",
        qualifier="test",
        codebuild_projects=[
            GitHubActionsRunner(
                owner="test-owner",
                repository="test-repo",
                gh_token_secret="test-secret",
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
                    compute_type=codebuild.ComputeType.SMALL,
                    privileged=True,
                ),
            ),
        ],
    )

    assert config.aws_account_id == "123456789012"
    assert config.aws_region == "us-west-2"
    assert config.qualifier == "test"
    assert len(config.codebuild_projects) == 1
    assert isinstance(config.codebuild_projects[0], GitHubActionsRunner)


def test_codebuild_environments() -> None:
    """Test that the predefined environments have the expected properties"""
    assert AMAZON_LINUX_SMALL.compute_type == codebuild.ComputeType.SMALL
    assert AMAZON_LINUX_MEDIUM.compute_type == codebuild.ComputeType.MEDIUM
    assert AMAZON_LINUX_LARGE.compute_type == codebuild.ComputeType.LARGE

    assert AMAZON_LINUX_SMALL.build_image.image_id.startswith(
        "aws/codebuild/amazonlinux2"
    )
    assert AMAZON_LINUX_MEDIUM.build_image.image_id.startswith(
        "aws/codebuild/amazonlinux2"
    )
    assert AMAZON_LINUX_LARGE.build_image.image_id.startswith(
        "aws/codebuild/amazonlinux2"
    )

    assert AMAZON_LINUX_SMALL.privileged is True
    assert AMAZON_LINUX_MEDIUM.privileged is True
    assert AMAZON_LINUX_LARGE.privileged is True
