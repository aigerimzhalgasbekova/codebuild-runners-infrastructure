import os

import aws_cdk as cdk
import pytest
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from aws_cdk.assertions import Capture, Match, Template
from constructs import Construct

from deploy.constructs.codebuild_project import CodeBuildProject, VpcAndSubnets
from deploy.lib.codebuild_dataclasses import GitHubActionsRunner
from deploy.lib.codebuild_environments import AMAZON_LINUX_SMALL

# Mock environment variables
os.environ["AWS_ACCOUNT_ID"] = "123456789012"
os.environ["AWS_REGION"] = "eu-west-1"
os.environ["AWS_CDK_BOOTSTRAP_QUALIFIER"] = "test-qualifier"
os.environ["GITHUB_TOKEN_SECRET_PATH"] = "test/github/token"


class VpcTestStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create test SSM parameters for VPC config
        vpc_id_param = ssm.StringParameter(
            self,
            "VpcIdParam",
            parameter_name="/shared/vpc-id",
            string_value="vpc-12345",
        )

        public_subnet_ids_param = ssm.StringParameter(
            self,
            "PublicSubnetIdsParam",
            parameter_name="/shared/public-subnet-ids",
            string_value="subnet-public1,subnet-public2",
        )

        private_subnet_ids_param = ssm.StringParameter(
            self,
            "PrivateSubnetIdsParam",
            parameter_name="/shared/private-subnet-ids",
            string_value="subnet-private1,subnet-private2",
        )

        # Create test VPC
        vpc = ec2.Vpc.from_lookup(
            self,
            "TestVpc",
            vpc_id="vpc-12345",
        )

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
    stack = VpcTestStack(
        app,
        "TestVpcStack",
        env=cdk.Environment(account="123456789012", region="eu-west-1"),
    )
    return Template.from_stack(stack)


def test_vpc_parameters_lookup(template):
    # Verify that the SSM parameters are created
    template.resource_count_is("AWS::SSM::Parameter", 3)

    # Check that the parameter names are correct
    vpc_id_capture = Capture()
    public_subnets_capture = Capture()
    private_subnets_capture = Capture()

    template.has_resource_properties(
        "AWS::SSM::Parameter", {"Name": vpc_id_capture, "Value": "vpc-12345"}
    )

    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {"Name": public_subnets_capture, "Value": "subnet-public1,subnet-public2"},
    )

    template.has_resource_properties(
        "AWS::SSM::Parameter",
        {"Name": private_subnets_capture, "Value": "subnet-private1,subnet-private2"},
    )

    assert vpc_id_capture.as_string() == "/shared/vpc-id"
    assert public_subnets_capture.as_string() == "/shared/public-subnet-ids"
    assert private_subnets_capture.as_string() == "/shared/private-subnet-ids"


def test_codebuild_project_vpc_config(template):
    # First verify that the CodeBuild project has a VPC ID
    template.has_resource_properties(
        "AWS::CodeBuild::Project", {"VpcConfig": {"VpcId": "vpc-12345"}}
    )

    # Then separately verify the Subnets and SecurityGroupIds exist
    resources = template.find_resources("AWS::CodeBuild::Project")
    for resource_id, resource in resources.items():
        properties = resource.get("Properties", {})
        vpc_config = properties.get("VpcConfig", {})

        assert "Subnets" in vpc_config, "Subnets should be defined in VpcConfig"
        assert isinstance(vpc_config["Subnets"], list), "Subnets should be a list"
        assert len(vpc_config["Subnets"]) > 0, "Subnets list should not be empty"

        assert (
            "SecurityGroupIds" in vpc_config
        ), "SecurityGroupIds should be defined in VpcConfig"
        assert isinstance(
            vpc_config["SecurityGroupIds"], list
        ), "SecurityGroupIds should be a list"
        assert (
            len(vpc_config["SecurityGroupIds"]) > 0
        ), "SecurityGroupIds list should not be empty"
