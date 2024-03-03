from typing import Dict, List

from fastapi import FastAPI

from api.db import create_new_request, get_latest_request, update_request_by_id
from api.multion import MarketplaceAssistant  # noqa

app = FastAPI()


@app.get("/")
async def hello():
    return {"message": "Hello World"}


@app.post("/query")
async def query(prompt: str):
    """
    Endpoint to handle queries to the MarketplaceAssistant.

    :param prompt: The query string to be used for searching the marketplace.
    :return: A JSON list of matching marketplace items.
    """
    agent = MarketplaceAssistant()
    return await agent.filter(prompt)


@app.post("/message_seller")
async def message_seller(url: str):
    """
    Endpoint to handle messages to sellers on Facebook Marketplace.

    :param urls: A list of URLs to be used for messaging the sellers.
    :return: A JSON list of messages sent to the sellers.
    """
    agent = MarketplaceAssistant()
    return await agent.message_seller(url)


def get_text(body: Dict) -> str:
    return "Hello World"


def get_media(body: Dict) -> List[str]:
    return ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]


def start_agent():
    pass


@app.api_route("/sms_webhook", methods=["POST", "GET"])
async def sms_webhook(body: Dict):
    text = get_text(body)
    media = get_media(body)

    latest_request = get_latest_request()

    started = False

    if latest_request is None or latest_request.started:
        if text is not None and text.lower() == "start":
            # TODO
            return "please provide instructions"
        create_new_request(text, {i: media[i] for i in range(len(media))})
    else:
        if text.lower() == "start":
            started = True
            new_text = latest_request.text
        elif text is not None:
            new_text = latest_request.text + "\n" + text
        if media is not None and len(media) > 0:
            updated_media_list = list(latest_request.media.values()) + media
            updated_media = {
                i: updated_media_list[i] for i in range(len(updated_media_list))
            }
        update_request_by_id(latest_request.id, new_text, updated_media, started)

    if started:
        start_agent()
