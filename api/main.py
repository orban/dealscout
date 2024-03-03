from fastapi import FastAPI, HTTPException, Request as APIRequest, Response, BackgroundTasks
from api.image_ranker import ImageRanker
from api.facebook_marketplace_scraper import FacebookMarketplaceScraper
from typing import Dict, List
from pydantic import BaseModel
from api.db import create_new_request, get_latest_request, update_request_by_id
from api.multion import MarketplaceAssistant  # noqa
import api.whatsapp as whatsapp

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


class ScrapeMarketplaceRequest(BaseModel):
    url: str
    reference_image_urls: List[str]


@app.post("/scrape_marketplace")
async def scrape_marketplace(request: ScrapeMarketplaceRequest):
    scraper = FacebookMarketplaceScraper(headless=False)
    items = await scraper.scrape(request.url)
    try:
        # Initialize the ranker
        ranker = ImageRanker()
        results = ranker.rank_images(request.reference_image_urls, items)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def ranker(url: str, media: List[str]):
    pass


def message_user(phone: str, urls: List[str]):
    pass


async def start_shopping(phone: str, prompt: str, media: List[str] = []):
    agent = MarketplaceAssistant()
    filter_res = await agent.filter(prompt)
    search_url = filter_res['url']
    product_urls = await ranker(search_url, media)
    await agent.message_seller(product_urls)
    message_user(phone, product_urls)


@app.api_route("/sms_webhook", methods=["POST", "GET"])
async def sms_webhook(request: APIRequest, background_tasks: BackgroundTasks):
    if request.method == "GET":
        challenge = request.query_params.get("hub.challenge")
        return Response(content=challenge, status_code=200, headers={"Content-Type": "text/plain"})

    body = await request.json()
    text = whatsapp.get_text(body)
    media = whatsapp.get_media(body)
    phone = whatsapp.get_phone(body)

    print(f"Text: {text}")
    print(f"Media: {media}")
    print(f"Phone: {phone}")

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
            updated_media = {i: updated_media_list[i]
                             for i in range(len(updated_media_list))}
        else:
            updated_media = latest_request.media
        update_request_by_id(latest_request.id, new_text,
                             updated_media, started)
        if started:
            print("Starting marketplace agent with prompt:", latest_request.text)
            background_tasks.add_task(
                start_shopping, phone, latest_request.text, media)
        return "ok"
