"""
Kernelsoul - AI Bridge (DeepSeek API)
Uses OpenAI-compatible client for non-streaming calls.
"""
from openai import OpenAI


class AIBridge:
    """AI API bridge - connects to DeepSeek via OpenAI-compatible endpoint."""

    def __init__(self, config: dict):
        self.api_key = config.get("api_key", "")
        self.api_base = config.get("api_base", "https://api.deepseek.com")
        self.model = config.get("model", "deepseek-v4-flash")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.8)

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
            )
        else:
            self.client = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Non-streaming call to DeepSeek API.

        Args:
            system_prompt: System-level instructions (character + game rules)
            user_prompt: Assembled context (state + recent log + worldbook + user input)

        Returns:
            Raw AI response text, or error message string on failure.
        """
        if not self.client:
            return "[ERROR] No API key configured. Set api_key in configs/system.json"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'[ERROR] API call failed: {e}'

    def generate_raw(self, messages: list) -> str:
        """Call API with pre-built message list."""
        if not self.client:
            return "[ERROR] No API key configured."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'[ERROR] API call failed: {e}'

    def generate_stream(self, system_prompt: str, user_prompt: str):
        """Streaming API call. Yields tokens one at a time."""
        if not self.client:
            yield "[ERROR] No API key configured."
            return
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            yield f"[ERROR] {e}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts using the configured API.
        Uses DeepSeek/OpenAI-compatible embeddings endpoint.
        Each result is [dim] floats.
        """
        # Build embeddings-compatible client
        client_kwargs = {"api_key": self.api_key, "base_url": self.api_base}
        emb_client = OpenAI(**client_kwargs)
        try:
            resp = emb_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [d.embedding for d in resp.data]
        except Exception:
            # Try alternate model names
            for alt_model in ["text-embedding-3-small", "bge-base"]:
                try:
                    resp = emb_client.embeddings.create(
                        model=alt_model, input=texts
                    )
                    return [d.embedding for d in resp.data]
                except Exception:
                    continue
            raise RuntimeError(
                "Embedding API unavailable. Check API key and model availability."
            )