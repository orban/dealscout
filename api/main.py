from fastapi import FastAPI, HTTPException, Request as APIRequest, Response, BackgroundTasks
from loguru import logger
from api.image_ranker import ImageRanker
from api.facebook_marketplace_scraper import FacebookMarketplaceScraper
from typing import Dict, List
from api.db import create_new_request, get_latest_request, update_request_by_id
from api.multion import MarketplaceAssistant  # noqa
import api.whatsapp as whatsapp

app = FastAPI()


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


async def start_shopping(phone: str, prompt: str, media: List[str] = []):
    agent = MarketplaceAssistant()
    filter_res = await agent.filter(prompt)
    search_url = filter_res['url']
    product_urls = await scrape_marketplace(search_url, media)
    for url in product_urls:
        await agent.message_seller(url)
        whatsapp.message_user(phone, url)


@app.api_route("/sms_webhook", methods=["POST", "GET"])
async def sms_webhook(request: APIRequest, background_tasks: BackgroundTasks):
    if request.method == "GET":
        challenge = request.query_params.get("hub.challenge")
        return Response(content=challenge, status_code=200, headers={"Content-Type": "text/plain"})

    body = await request.json()
    logger.debug("Received body:", body)
    text = whatsapp.get_text(body)
    media = whatsapp.get_media(body)
    phone = whatsapp.get_phone(body)

    if not phone:
        return

    logger.debug(f"Text: {text}")
    logger.debug(f"Media: {media}")
    logger.debug(f"Phone: {phone}")

    latest_request = get_latest_request()

    started = False

    if latest_request is None or latest_request.started:
        logger.debug("Starting new request")
        if text is not None and text.lower() == "start":
            whatsapp.message_user(
                phone, """Welcome to the Marketplace Assistant! Please describe what you're looking for. 
                You can also send images to help us find the best matches. When you're ready, type 'start' to begin.""")
        create_new_request(text, {i: media[i] for i in range(len(media))})
    else:
        logger.debug(f"Continuing current request {latest_request.id}")
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
        logger.debug("Starting marketplace agent with prompt:",
                     latest_request.text)
        whatsapp.message_user(
            phone, "🫡 We're on it! We'll let you know when we find some matches.")
        background_tasks.add_task(
            start_shopping, phone, latest_request.text, media)
    else:
        whatsapp.message_user(
            phone, "Understood! Type 'start' when you're done providing instructions and we'll begin shopping.")
    return
