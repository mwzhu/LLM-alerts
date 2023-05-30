"""Server for demo app showing how to use multiple local models."""

import os
import openai
import dotenv
from flask import Flask, jsonify, request
from langchain.chat_models import ChatOpenAI
from llama_index import Document, GPTVectorStoreIndex, LLMPredictor, ServiceContext
# from transformers import pipeline
from webdrive_llm import web_drive_LLM



dotenv.load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

LOCAL_INDEX_FILE = "code_snippet_index.json"

app = Flask(__name__)

@app.route("/completions", methods=["POST"])
def completions():
    """The completions endpoint."""
    # Get the request data.
    data = request.get_json()
    prompt = data["prompt"]
    model = data["model"]
    print(prompt)
    print(model)

    if model not in ["langwallet", "gpt-4", "gpt-3.5-turbo"]:
        return jsonify({"error": f"Could not find model {model}."})

    if model == "embedding":
        # Embed the input.
        documents = [Document(prompt)]
        index = GPTVectorStoreIndex.from_documents(documents)
        index.save_to_disk(LOCAL_INDEX_FILE)
        ret_data = {
            "choices": [
                {"text": "Successfully embedded."}
            ]
        }
    elif model == "langwallet":
        # Ask ChatGPT for the output.
        langwallet_res = web_drive_LLM("show me the holdings of vitlaik.eth")
        # llm = ChatOpenAI(model_name="gpt-3.5-turbo")
        # llm_predictor = LLMPredictor(llm=llm)
        # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
        # index = GPTVectorStoreIndex.load_from_disk(
        #     LOCAL_INDEX_FILE, service_context=service_context
        # )
        # response = index.query(prompt)

        #responds to window
        #TODO: How to return image to windowai?
        #example langwallet_res: ['vitalik.eth_tokens.png', 'https://app.zerion.io/vitalik.eth/tokens']
        ret_data = {
            "choices": [
                {"text": langwallet_res }
            ]
        }

    print(ret_data)
    return jsonify(ret_data)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)