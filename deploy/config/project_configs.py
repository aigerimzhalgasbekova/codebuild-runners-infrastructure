from ..lib.codebuild_dataclasses import GitHubActionsRunner
from .environment import (
    AWS_ACCOUNT_ID,
    AWS_CDK_BOOTSTRAP_QUALIFIER,
    GITHUB_TOKEN_SECRET_PATH,
)

project_configs: list[GitHubActionsRunner] = [
    GitHubActionsRunner(
        allowed_roles=[
            f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/cdk-{AWS_CDK_BOOTSTRAP_QUALIFIER}-*",
        ],
        gh_token_secret=GITHUB_TOKEN_SECRET_PATH,
        owner="aigerimzhalgasbekova",
        repository="auth-api",
    )
]
