"""CodeBuild project construct implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aws_cdk import Aws, Duration, RemovalPolicy, SecretValue
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from ..lib.codebuild_dataclasses import CodeBuildProjectConfig


@dataclass
class VpcAndSubnets:
    """Data class to hold VPC and subnet configuration.

    Attributes:
        vpc: The VPC where the CodeBuild project will run
        public_subnets: List of public subnets in the VPC
        private_subnets: List of private subnets where CodeBuild projects will run
    """

    vpc: ec2.Vpc
    public_subnets: list[ec2.Subnet]
    private_subnets: list[ec2.Subnet]


class CodeBuildProject(Construct):
    """Construct that creates an AWS CodeBuild project for GitHub Actions runners.

    This construct sets up a CodeBuild project with the following features:
    - VPC configuration with private subnet deployment
    - GitHub webhook integration
    - CloudWatch logging
    - IAM roles and policies
    - GitHub credentials management

    Attributes:
        project_arn: The ARN of the created CodeBuild project
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_spec: CodeBuildProjectConfig,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the CodeBuild project construct.

        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            project_spec: Configuration for the CodeBuild project
            **kwargs: Additional arguments to pass to the parent construct
        """
        super().__init__(scope, construct_id, **kwargs)

        vpc_and_subnets = self.get_vpc_and_subnets(scope, construct_id)
        # Create a CodeBuild project
        build_project = codebuild.Project(
            self,
            construct_id,
            project_name=construct_id,
            environment=project_spec.build_environment,
            vpc=vpc_and_subnets.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnets=vpc_and_subnets.private_subnets
            ),
            source=codebuild.Source.git_hub(
                owner=project_spec.owner,
                repo=project_spec.repository,
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(
                        codebuild.EventAction.WORKFLOW_JOB_QUEUED,
                    )
                ],
            ),
            timeout=Duration.minutes(15),
            logging=codebuild.LoggingOptions(
                cloud_watch=codebuild.CloudWatchLoggingOptions(
                    enabled=True,
                    log_group=logs.LogGroup(
                        self,
                        f"{construct_id}-log-group",
                        log_group_name=f"/aws/codebuild/{construct_id}",
                        removal_policy=RemovalPolicy.DESTROY,
                    ),
                )
            ),
        )

        # Create GitHub Credentials if token is provided
        if project_spec.gh_token_secret:
            codebuild.GitHubSourceCredentials(
                self,
                f"{construct_id}-gh-creds",
                access_token=SecretValue.secrets_manager(project_spec.gh_token_secret),
            )

            # Allow the project to access the GitHub repository
            build_project.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                    ],
                    resources=[
                        f"arn:aws:secretsmanager:{Aws.REGION}:{Aws.ACCOUNT_ID}:secret:{project_spec.gh_token_secret}-*"
                    ],
                )
            )

        # Allow the specified roles to execute the project
        if project_spec.allowed_roles:
            build_project.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=project_spec.allowed_roles,
                )
            )

        build_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[
                    "arn:aws:s3:::az-artifacts-bucket",
                    "arn:aws:s3:::az-artifacts-bucket/*",
                ],
            )
        )

        # Output the project ARN
        self.project_arn = build_project.project_arn

    def get_vpc_and_subnets(self, scope: Construct, construct_id: str) -> VpcAndSubnets:
        """Retrieve VPC and subnet configuration from SSM Parameter Store.

        This method looks up the VPC ID and subnet IDs from SSM Parameter Store
        and creates the necessary VPC and subnet objects.

        Args:
            scope: The scope in which to define the VPC and subnet objects
            construct_id: The construct ID to use for resource naming

        Returns:
            VpcAndSubnets object containing the VPC and subnet configuration

        Raises:
            ValueError: If required SSM parameters are not found
        """
        # Retrieve SSM parameters storing VPC ID and subnet IDs
        vpc_id_param = ssm.StringParameter.value_from_lookup(scope, "/shared/vpc-id")
        public_subnet_ids_param = ssm.StringParameter.value_from_lookup(
            scope, "/shared/public-subnet-ids"
        )
        private_subnet_ids_param = ssm.StringParameter.value_from_lookup(
            scope, "/shared/private-subnet-ids"
        )

        # Create subnet objects
        public_subnets = [
            ec2.Subnet.from_subnet_id(
                scope, f"{construct_id}-public-{subnet_id}", subnet_id
            )
            for subnet_id in public_subnet_ids_param.split(",")
        ]
        privet_subnets = [
            ec2.Subnet.from_subnet_id(
                scope, f"{construct_id}-private-{subnet_id}", subnet_id
            )
            for subnet_id in private_subnet_ids_param.split(",")
        ]
        # Lookup VPC
        vpc = ec2.Vpc.from_lookup(scope, f"{construct_id}-vpc", vpc_id=vpc_id_param)

        return VpcAndSubnets(
            vpc=vpc, private_subnets=privet_subnets, public_subnets=public_subnets
        )
