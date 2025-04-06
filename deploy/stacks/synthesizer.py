from aws_cdk import DefaultStackSynthesizer, Stack
from constructs import Construct


class StackSynthesizer(DefaultStackSynthesizer):
    """Custom stack synthesizer for CodeBuild projects.

    This synthesizer extends the default CDK stack synthesizer to add
    custom tags and naming conventions for the CodeBuild infrastructure.

    Attributes:
        qualifier: The qualifier used for resource naming
    """

    def __init__(self, qualifier: str) -> None:
        """Initialize the stack synthesizer.

        Args:
            qualifier: The qualifier to use for resource naming
        """
        super().__init__(qualifier=qualifier)
