import boto3
import os
import re
from typing import List
from botocore.exceptions import ClientError
from app.chatbot.aiAgent.AiAgent import AiAgent



class AwsAgent:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
 
        # 🔴 NO usar amazon.nova-lite-v1:0
        # ✅ Usar ARN del inference profile
        self.model_id = os.getenv(
            "AWS_BEDROCK_MODEL_ID",
            "arn:aws:bedrock:us-east-1::inference-profile/amazon-nova-lite-v1"
        )

        # Validate model identifier early and provide clearer errors
        self._validate_model_id(self.model_id)

        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )

    def _validate_model_id(self, model_id: str):
        """Validate common incorrect model id formats and provide actionable error messages."""
        if not model_id:
            raise ValueError(
                "AWS_BEDROCK_MODEL_ID is not set. Set it to the inference profile ARN, e.g. arn:aws:bedrock:REGION::inference-profile/NAME."
            )
        # If user provided a short model name like 'amazon.nova-lite-v1' or 'amazon.nova-lite-v1:0', reject it
        short_model_pattern = re.compile(r"^amazon\.[a-z0-9\-]+(:\d+)?$")
        if short_model_pattern.match(model_id) or (":" in model_id and not model_id.startswith("arn:")):
            raise ValueError(
                "Invalid Bedrock model identifier provided in AWS_BEDROCK_MODEL_ID. "
                "Use the inference profile ARN (e.g. arn:aws:bedrock:REGION::inference-profile/NAME) "
                "instead of short model names like 'amazon.nova-lite-v1' or 'amazon.nova-lite-v1:0'."
            )
        # Basic ARN sanity check
        if not model_id.startswith("arn:aws:bedrock:"):
            raise ValueError(
                "AWS_BEDROCK_MODEL_ID does not look like a Bedrock ARN. "
                "Expected format: arn:aws:bedrock:<region>::inference-profile/<name>."
            )

    def respond(self, history: List[dict]) -> str:
        messages = [
            {
                "role": m["role"],
                "content": [{"text": m["content"]}]
            }
            for m in history
        ]

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": 512,
                    "temperature": 0.5
                }
            )
        except ClientError as e:
            # Provide a concise, actionable error to the caller
            raise RuntimeError(
                f"AWS Bedrock Converse failed for model '{self.model_id}': {e.response.get('Error', {}).get('Message', str(e))}"
            ) from e

        try:
            return response["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError("Unexpected response structure from Bedrock converse call") from e

