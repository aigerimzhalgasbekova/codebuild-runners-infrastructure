import os

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Match, Template

from deploy.lib.codebuild_dataclasses import EnvConfig, GitHubActionsRunner
from deploy.stacks.codebuild_projects_stack import CodeBuildProjectStack

# Mock environment variables
os.environ["AWS_ACCOUNT_ID"] = "123456789012"
os.environ["AWS_REGION"] = "eu-west-1"
os.environ["AWS_CDK_BOOTSTRAP_QUALIFIER"] = "test-qualifier"
os.environ["GITHUB_TOKEN_SECRET_PATH"] = "test/github/token"


@pytest.fixture
def template():
    app = cdk.App()

    # Create a test environment config
    env_config = EnvConfig(
        aws_account_id="123456789012",
        aws_region="eu-west-1",
        qualifier="test-qualifier",
        codebuild_projects=[
            GitHubActionsRunner(
                allowed_roles=[
                    "arn:aws:iam::123456789012:role/cdk-test-qualifier-*",
                ],
                gh_token_secret="test/github/token",
                owner="test-owner",
                repository="test-repo",
            )
        ],
    )

    # Create the stack
    stack = CodeBuildProjectStack(
        app,
        "TestStack",
        env_config,
        env=cdk.Environment(account="123456789012", region="eu-west-1"),
    )

    return Template.from_stack(stack)


def test_stack_creates_codebuild_project(template):
    # Verify that the CodeBuild project is created
    template.resource_count_is("AWS::CodeBuild::Project", 1)

    # Verify project properties based on our test config
    template.has_resource_properties(
        "AWS::CodeBuild::Project",
        {
            "Name": "test-owner-test-repo",
            "Source": {
                "Type": "GITHUB",
                "Location": "https://github.com/test-owner/test-repo.git",
            },
        },
    )


def test_stack_creates_log_group(template):
    # Verify that the CloudWatch Logs group is created
    template.resource_count_is("AWS::Logs::LogGroup", 1)

    # Verify log group name contains our project name
    template.has_resource_properties(
        "AWS::Logs::LogGroup",
        {
            "LogGroupName": "/aws/codebuild/test-owner-test-repo",
        },
    )
