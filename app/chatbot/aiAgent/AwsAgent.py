import boto3
import os
import re
from typing import List
from botocore.exceptions import ClientError
from app.chatbot.aiAgent.AiAgent import AiAgent



class AwsAgent(AiAgent):
    def __init__(self):
        super().__init__()  # Initialize parent class
        
        # Load pricing from environment variables
        self.input_price_per_1k_tokens = float(os.getenv("AWS_INPUT_PRICE_PER_1K_TOKENS", "0.0008"))
        self.output_price_per_1k_tokens = float(os.getenv("AWS_OUTPUT_PRICE_PER_1K_TOKENS", "0.0032"))
        
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        # DO NOT use amazon.nova-lite-v1:0
        # Use ARN of the inference profile
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
        # Use smart history management for AWS
        # Get the current request_id from the last message if available
        current_request_id = None
        if history and len(history) > 0:
            last_msg = history[-1]
            if isinstance(last_msg, dict) and 'request_id' in last_msg:
                current_request_id = last_msg.get('request_id')
        
        # If we have MongoDB access, use smart history
        try:
            from app.chatbot.memory.MongoMemory import MongoMemory
            mongo = MongoMemory()
            
            # Get session_id from history context (this is a bit hacky, but works)
            session_id = None
            for msg in history:
                if isinstance(msg, dict) and 'session_id' in msg:
                    session_id = msg['session_id']
                    break
            
            if session_id and current_request_id:
                # Use smart history that includes context but avoids repetition
                smart_history = mongo.get_smart_history(session_id, current_request_id)
                
                # Convert MongoDB messages to the format expected by AWS
                messages = []
                for msg in smart_history:
                    if msg["role"] in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": [{"text": msg["content"]}]
                        })
                
                # If no smart history, fall back to current message only
                if not messages and history:
                    last_user_msg = None
                    for msg in reversed(history):
                        if msg.get("role") == "user":
                            last_user_msg = msg
                            break
                    
                    if last_user_msg:
                        messages = [{
                            "role": "user",
                            "content": [{"text": last_user_msg["content"]}]
                        }]
            else:
                # Fallback: use only the last user message
                messages = []
                if history:
                    last_user_msg = None
                    for msg in reversed(history):
                        if msg.get("role") == "user":
                            last_user_msg = msg
                            break
                    
                    if last_user_msg:
                        messages = [{
                            "role": "user",
                            "content": [{"text": last_user_msg["content"]}]
                        }]
        
        except Exception as e:
            print(f"Warning: Could not use smart history, falling back to simple approach: {e}")
            # Fallback: use only the last user message
            messages = []
            if history:
                last_user_msg = None
                for msg in reversed(history):
                    if msg.get("role") == "user":
                        last_user_msg = msg
                        break
                
                if last_user_msg:
                    messages = [{
                        "role": "user",
                        "content": [{"text": last_user_msg["content"]}]
                    }]

        # Enhanced system prompt for better context handling
        system_prompt = """You are a helpful AI assistant. IMPORTANT INSTRUCTIONS:
1. Answer the current question directly and completely
2. Remember important context from the conversation (like the user's name if mentioned)
3. Do NOT repeat answers to questions that were already asked and answered
4. Provide thorough, complete responses within the token limit
5. If the user introduced themselves earlier, remember their name
6. Each response should be comprehensive and helpful"""

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": 3000,  # Increased further to prevent JavaScript truncation
                    "temperature": 0.2  # Lower temperature for more consistent responses
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

