
from fastapi import FastAPI, HTTPException, UploadFile, File
from .image_ranker import ImageRanker
from typing import List
from .facebook_marketplace_scraper import FacebookMarketplaceScraper
from typing import Dict, List

from api.db import create_new_request, get_latest_request, update_request_by_id
from api.multion import MarketplaceAssistant  # noqa

app = FastAPI()


@app.post("/rank_images")
async def rank_images_endpoint(reference_image_urls: List[str], candidate_images: List[str]):
    try:
        # Initialize the ranker
        ranker = ImageRanker()
        results = ranker.rank_images(reference_image_urls, candidate_images)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape_marketplace")
async def scrape_marketplace(url: str, reference_image_urls: List[str]):
    scraper = FacebookMarketplaceScraper(headless=False)
    items = await scraper.scrape(url)
    try:
        # Initialize the ranker
        ranker = ImageRanker()
        results = ranker.rank_images(reference_image_urls, items)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        update_request_by_id(latest_request.id, new_text,
                             updated_media, started)

    if started:
        start_agent()
