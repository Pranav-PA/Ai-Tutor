"""AI Provider service - supports OpenAI, Google Gemini, and Ollama (local)."""
import os
from typing import List, Optional, AsyncGenerator
import json
import httpx

from backend.config import (
    OPENAI_API_KEY, GEMINI_API_KEY, DEFAULT_PROVIDER,
    OPENAI_MODEL, GEMINI_MODEL,
    TEACHING_TEMPERATURE, QUIZ_TEMPERATURE, GENERAL_TEMPERATURE
)

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")


def get_provider() -> str:
    """Get the current AI provider."""
    # Check environment/settings
    provider = os.getenv("AI_PROVIDER", DEFAULT_PROVIDER)
    
    if provider == "ollama":
        return "ollama"
    if provider == "openai" and OPENAI_API_KEY:
        return "openai"
    elif provider == "gemini" and GEMINI_API_KEY:
        return "gemini"
    # Fallback
    if OPENAI_API_KEY:
        return "openai"
    if GEMINI_API_KEY:
        return "gemini"
    # Default to ollama if no API keys
    return "ollama"


def get_available_providers() -> List[dict]:
    """Get list of available AI providers and their status."""
    providers = []
    
    # OpenAI
    providers.append({
        "id": "openai",
        "name": "OpenAI (GPT)",
        "available": bool(OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")),
        "requires_api_key": True,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    })
    
    # Gemini
    providers.append({
        "id": "gemini",
        "name": "Google Gemini",
        "available": bool(GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")),
        "requires_api_key": True,
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
    })
    
    # Ollama (local)
    ollama_available = False
    ollama_models = []
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        if response.status_code == 200:
            ollama_available = True
            data = response.json()
            ollama_models = [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    
    providers.append({
        "id": "ollama",
        "name": "Ollama (Local)",
        "available": ollama_available,
        "requires_api_key": False,
        "models": ollama_models or ["llama3.1", "llama3.1:8b", "mistral", "codellama", "phi3"]
    })
    
    return providers


def get_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    """Generate embeddings for a list of texts."""
    provider = get_provider()

    try:
        if provider == "openai" and OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]

        elif provider == "gemini" and GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text
                )
                embeddings.append(result['embedding'])
            return embeddings

        elif provider == "ollama":
            # Use Ollama embeddings
            embeddings = []
            for text in texts:
                response = httpx.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json={"model": OLLAMA_MODEL, "prompt": text},
                    timeout=30.0
                )
                if response.status_code == 200:
                    embeddings.append(response.json().get("embedding", []))
                else:
                    return None
            return embeddings if embeddings else None

    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def chat_completion(
    messages: List[dict],
    temperature: float = GENERAL_TEMPERATURE,
    max_tokens: int = 4096,
    provider: Optional[str] = None
) -> str:
    """Generate a chat completion."""
    provider = provider or get_provider()

    if provider == "openai" and OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    elif provider == "gemini" and GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Convert messages to Gemini format
        gemini_messages = []
        system_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        # Prepend system to first user message if exists
        if system_prompt and gemini_messages:
            gemini_messages[0]["parts"][0] = f"{system_prompt}\n\n{gemini_messages[0]['parts'][0]}"

        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        response = chat.send_message(
            gemini_messages[-1]["parts"][0] if gemini_messages else "Hello",
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return response.text

    elif provider == "ollama":
        # Use Ollama local model
        ollama_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        ollama_model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
        
        try:
            response = httpx.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120.0
            )
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return f"Ollama error: {response.status_code} - {response.text}"
        except httpx.ConnectError:
            return "Ollama is not running. Please start Ollama first (https://ollama.ai) or switch to an API provider in Settings."
        except Exception as e:
            return f"Ollama error: {str(e)}"

    else:
        return "No AI provider configured. Please add your API key in settings or start Ollama for local models."


async def stream_chat_completion(
    messages: List[dict],
    temperature: float = GENERAL_TEMPERATURE,
    max_tokens: int = 4096,
    provider: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Stream a chat completion response."""
    provider = provider or get_provider()

    if provider == "openai" and OPENAI_API_KEY:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    elif provider == "gemini" and GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        gemini_messages = []
        system_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        if system_prompt and gemini_messages:
            gemini_messages[0]["parts"][0] = f"{system_prompt}\n\n{gemini_messages[0]['parts'][0]}"

        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        response = chat.send_message(
            gemini_messages[-1]["parts"][0] if gemini_messages else "Hello",
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            stream=True
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    elif provider == "ollama":
        # Stream from Ollama local model
        ollama_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        ollama_model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{ollama_url}/api/chat",
                    json={
                        "model": ollama_model,
                        "messages": messages,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield content
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except httpx.ConnectError:
            yield "Ollama is not running. Please start Ollama first (https://ollama.ai) or switch to an API provider in Settings."
        except Exception as e:
            yield f"Ollama error: {str(e)}"

    else:
        yield "No AI provider configured. Please add your API key in settings or start Ollama for local models."


def json_completion(
    messages: List[dict],
    temperature: float = GENERAL_TEMPERATURE,
    provider: Optional[str] = None
) -> dict:
    """Generate a structured JSON response."""
    provider = provider or get_provider()

    # Add JSON instruction to system message
    json_instruction = "\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, just raw JSON."
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] += json_instruction
    else:
        messages.insert(0, {"role": "system", "content": json_instruction})

    response = chat_completion(messages, temperature=temperature, provider=provider)

    # Parse JSON from response
    try:
        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        try:
            start = response.index('{')
            end = response.rindex('}') + 1
            return json.loads(response[start:end])
        except (ValueError, json.JSONDecodeError):
            return {"error": "Failed to parse AI response", "raw": response}
