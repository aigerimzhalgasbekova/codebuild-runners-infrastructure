"""Pre-configured AWS CodeBuild environments.

This module provides standard build environments for CodeBuild projects,
configured with Amazon Linux 2 and different compute types.
"""

from aws_cdk import aws_codebuild as codebuild

# Small compute type build environment (2 vCPU, 4 GB RAM)
AMAZON_LINUX_SMALL = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
    compute_type=codebuild.ComputeType.SMALL,
    privileged=True,
)

# Medium compute type build environment (4 vCPU, 8 GB RAM)
AMAZON_LINUX_MEDIUM = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
    compute_type=codebuild.ComputeType.MEDIUM,
    privileged=True,
)

# Large compute type build environment (8 vCPU, 16 GB RAM)
AMAZON_LINUX_LARGE = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
    compute_type=codebuild.ComputeType.LARGE,
    privileged=True,
)
