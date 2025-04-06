"""Configuration for the CodeBuild infrastructure."""

from typing import cast

from ..lib.codebuild_dataclasses import CodeBuildProjectConfig
from .environment import get_environment_config
from .project_configs import project_configs

# Cast to the base class type expected by the function
env_config = get_environment_config(
    cast("list[CodeBuildProjectConfig]", project_configs)
)
