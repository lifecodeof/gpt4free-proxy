import json
import random
import string
import time
from typing import Any

from flask import Flask, request
from flask_cors import CORS
from g4f import ChatCompletion, Provider, models as ms
from g4f.models import ModelUtils
from rich import print
from rich.json import JSON
from rich.panel import Panel
from rich.pretty import Pretty


app = Flask(__name__)
CORS(app)

providerIndex = 0
providers = Provider.__all__[1:]
models = list(ModelUtils.convert.keys())


def get_provider():
    return getattr(Provider, (providers[providerIndex]))


def prompt(model: str, stream: bool, messages):
    global providerIndex
    response = None
    provider = get_provider()
    try:
        response = ChatCompletion.create(
            model=model, stream=stream, messages=messages, provider=provider
        )
    except Exception as e:
        print(f"Error ({provider=}): {e}")

    if (
        not response
        or ("g4f.Provider.Providers" in response and "is not working" in response)
        or "AI.LS: FREE LIMIT EXCEEDED" in response
    ):
        providerIndex += 1
        providerIndex %= len(providers)
        print("NEXT_PROVIDER", providerIndex, get_provider())
        return prompt(model, stream, messages)
    else:
        return response


def rich_repr(obj):
    if type(obj) == str:
        try:
            return JSON(obj)
        except:
            return obj
    return Pretty(obj)


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    model = request.get_json().get("model", "gpt-3.5-turbo")
    stream = request.get_json().get("stream", False)
    messages = request.get_json().get("messages")
    print(Panel(Pretty(messages), title="messages"))

    response = prompt(model, stream, messages)

    completion_id = "".join(random.choices(string.ascii_letters + string.digits, k=28))
    completion_timestamp = int(time.time())

    if not stream:
        res = {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion",
            "created": completion_timestamp,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 1,
            },
        }
        print(Panel(rich_repr(response), title="response"))

        return res

    def streaming():
        for chunk in response:
            completion_data = {
                "id": f"chatcmpl-{completion_id}",
                "object": "chat.completion.chunk",
                "created": completion_timestamp,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": chunk,
                        },
                        "finish_reason": None,
                    }
                ],
            }

            content = json.dumps(completion_data, separators=(",", ":"))
            yield f"data: {content}\n\n"
            time.sleep(0.1)

        end_completion_data: dict[str, Any] = {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion.chunk",
            "created": completion_timestamp,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
        content = json.dumps(end_completion_data, separators=(",", ":"))
        yield f"data: {content}\n\n"

    return app.response_class(streaming(), mimetype="text/event-stream")


@app.get("/models")
def get_models():
    def model(id: str):
        return {
            "id": id,
            "object": "model",
            "created": 1686935002,
            "owned_by": "organization-owner",
        }

    return app.json.response(
        {
            "object": "list",
            "data": [model(id) for id in models],
            "object": "list",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=True)
