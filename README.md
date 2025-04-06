# AWS Codebuild Runners Infrastructure

This repository contains resources that enable the use of AWS Codebuild runners in GitHub Actions. It provides a scalable and secure way to run GitHub Actions workflows using AWS CodeBuild.

## Architecture

The infrastructure consists of the following components:

1. **CodeBuild Projects**
   - Each GitHub repository gets its own CodeBuild project
   - Projects run in a VPC with private subnets for enhanced security
   - CloudWatch Logs for build output and debugging
   - IAM roles with least-privilege permissions

2. **VPC Configuration**
   - Uses existing VPC infrastructure
   - CodeBuild projects run in private subnets
   - SSM Parameter Store for VPC and subnet configuration

3. **GitHub Integration**
   - Webhook-based triggers for GitHub Actions
   - Secure GitHub token storage in AWS Secrets Manager
   - Support for multiple repositories

4. **Security**
   - IAM roles with minimal required permissions
   - VPC isolation for build environments
   - Secrets management for GitHub tokens
   - Private subnet deployment

## Prerequisites

- Python 3.13+
- Poetry for dependency management
- AWS CLI configured with appropriate credentials
- AWS CDK v2
- An existing VPC with public and private subnets
- AWS Secrets Manager configured with GitHub tokens
- pre-commit for code quality enforcement

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and set the required values:
   - `AWS_ACCOUNT_ID`: Your AWS account ID
   - `AWS_REGION`: The AWS region to deploy to (defaults to eu-west-1)
   - `AWS_CDK_BOOTSTRAP_QUALIFIER`: The CDK bootstrap qualifier (defaults to hnb659fds)
   - `GITHUB_TOKEN_SECRET_PATH`: Path to the GitHub token in AWS Secrets Manager

3. Load the environment variables:
   ```bash
   export $(cat .env | grep -v '#' | xargs)
   ```

4. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

6. Install commit-msg hook for commit message validation:
   ```bash
   pre-commit install --hook-type commit-msg
   ```

7. Run pre-commit hooks on all files:
   ```bash
   pre-commit run --all-files
   ```

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd codebuild-runners-infrastructure
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Configure AWS credentials:
   ```bash
   aws configure
   ```

## Usage

### Adding a New Repository

1. Add a new repository configuration in `deploy/config/project_configs.py`:
   ```python
   GitHubActionsRunner(
       allowed_roles=[...],
       gh_token_secret="your-repo/github/token",
       owner="your-org",
       repository="your-repo"
   )
   ```

2. Deploy the updated configuration:
   ```bash
   cdk deploy
   ```

### Available Tasks

```bash
# Install dependencies
task setup

# Update dependencies
task poetry:lock

# Format code
task poetry:format

# Run tests
task test
task test:watch  # Run tests in watch mode
```

## Testing

The project uses pytest for unit testing:

```bash
# Run all tests
task test

# Run tests in watch mode during development
task test:watch
```

The tests use the AWS CDK assertions module to validate that the infrastructure is correctly defined:

- `test_codebuild_project.py` - Tests for the CodeBuildProject construct
- `test_codebuild_project_stack.py` - Tests for the CodeBuildProjectStack
- `test_vpc_and_subnets.py` - Tests for VPC and subnet configurations
- `test_codebuild_dataclasses.py` - Tests for the dataclass models

## Project Structure

```
.
├── deploy/
│   ├── config/           # Configuration and environment settings
│   ├── constructs/       # CDK constructs
│   ├── lib/             # Shared libraries and data models
│   └── stacks/          # CDK stacks
├── tests/               # Unit tests
├── app.py              # Main CDK app entry point
├── cdk.json           # CDK configuration
├── pyproject.toml     # Python dependencies
└── Taskfile.yaml     # Task runner configuration
```

## Security Considerations

1. **VPC Security**
   - CodeBuild projects run in private subnets
   - Network access is controlled through security groups
   - VPC endpoints for AWS services

2. **IAM Security**
   - Least-privilege principle for IAM roles
   - Separate roles for different repositories
   - Minimal required permissions for GitHub access

3. **Secrets Management**
   - GitHub tokens stored in AWS Secrets Manager
   - Secure access through IAM policies
   - No hardcoded credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run pre-commit hooks:
   ```bash
   pre-commit run --all-files
   ```
5. Run tests: `task test`
6. Format code: `task poetry:format`
7. Submit a pull request
