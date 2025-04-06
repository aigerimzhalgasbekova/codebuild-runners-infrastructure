import os

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Match, Template
from constructs import Construct

from deploy.constructs.codebuild_project import CodeBuildProject
from deploy.lib.codebuild_dataclasses import GitHubActionsRunner
from deploy.lib.codebuild_environments import AMAZON_LINUX_SMALL

# Mock environment variables
os.environ["AWS_ACCOUNT_ID"] = "123456789012"
os.environ["AWS_REGION"] = "eu-west-1"
os.environ["AWS_CDK_BOOTSTRAP_QUALIFIER"] = "test-qualifier"
os.environ["GITHUB_TOKEN_SECRET_PATH"] = "test/github/token"


class CodeBuildTestStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a test project spec
        project_spec = GitHubActionsRunner(
            allowed_roles=[
                f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/cdk-test-qualifier-*",
            ],
            gh_token_secret="test/github/token",
            owner="test-owner",
            repository="test-repo",
            build_environment=AMAZON_LINUX_SMALL,
        )

        # Create the CodeBuildProject construct
        CodeBuildProject(self, "TestProject", project_spec=project_spec)


@pytest.fixture
def template():
    app = cdk.App()
    stack = CodeBuildTestStack(
        app,
        "TestStack",
        env=cdk.Environment(account="123456789012", region="eu-west-1"),
    )
    return Template.from_stack(stack)


def test_codebuild_project_created(template):
    # Verify that the CodeBuild project is created
    template.resource_count_is("AWS::CodeBuild::Project", 1)

    # Verify project properties (relaxing the constraints)
    template.has_resource_properties(
        "AWS::CodeBuild::Project",
        {
            "Name": "TestProject",
            "Environment": {
                "Type": "LINUX_CONTAINER",
                "ComputeType": "BUILD_GENERAL1_SMALL",
                "PrivilegedMode": True,
            },
            "Source": {
                "Type": "GITHUB",
            },
            "TimeoutInMinutes": 15,
        },
    )


def test_codebuild_iam_role_permissions(template):
    # Verify that there are IAM policies created - using exact count instead of matcher
    template.resource_count_is("AWS::IAM::Policy", 2)

    # Check for S3 permissions which should always be present
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Action": "s3:PutObject",
                                "Effect": "Allow",
                                "Resource": Match.array_with(
                                    [
                                        "arn:aws:s3:::az-artifacts-bucket",
                                        "arn:aws:s3:::az-artifacts-bucket/*",
                                    ]
                                ),
                            }
                        )
                    ]
                )
            }
        },
    )


def test_codebuild_github_credentials(template):
    # Verify that GitHub credentials are created
    template.resource_count_is("AWS::CodeBuild::SourceCredential", 1)

    # Verify GitHub credentials properties
    template.has_resource_properties(
        "AWS::CodeBuild::SourceCredential",
        {"ServerType": "GITHUB", "AuthType": "PERSONAL_ACCESS_TOKEN"},
    )


def test_cloudwatch_logs_group(template):
    # Verify that CloudWatch Logs group is created
    template.resource_count_is("AWS::Logs::LogGroup", 1)

    # Verify log group properties
    template.has_resource_properties(
        "AWS::Logs::LogGroup",
        {"LogGroupName": Match.string_like_regexp("/aws/codebuild/TestProject")},
    )
