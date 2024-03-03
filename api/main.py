from typing import Any, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi import Request as APIRequest
from loguru import logger  # noqa

import api.whatsapp as whatsapp
from api.db import create_new_request, get_latest_request, update_request_by_id
from api.facebook_marketplace_scraper import FacebookMarketplaceScraper
from api.image_ranker import ImageRanker
from api.multion import MarketplaceAssistant

app = FastAPI()


async def scrape_marketplace(url: str, reference_image_urls: List[str]) -> Any:
    logger.debug(f"Scraping marketplace with URL: {url}")
    scraper = FacebookMarketplaceScraper(headless=True)
    try:
        items = await scraper.scrape(url)
        ranker = ImageRanker()
        rankings = ranker.rank_images(reference_image_urls, items)
        logger.debug(f"Rankings: {rankings}")
        return rankings
    except Exception as e:
        logger.exception("Failed to scrape marketplace.")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


async def start_shopping(
    phone: str, prompt: str, media: Optional[List[str]] = None
) -> None:
    media = media or []
    agent = MarketplaceAssistant()
    filter_res = await agent.filter(prompt)
    if search_url := filter_res.get("url"):
        product_urls = await scrape_marketplace(search_url, media)
        for url in product_urls:
            try:
                await agent.message_seller(url)
                whatsapp.message_user(phone, [url])
            except Exception as e:
                logger.exception(f"Error messaging seller for URL {url}. {e}")
    logger.debug(f"Marketplace assistant did not return valid URL {filter_res}")


@app.api_route("/sms_webhook", methods=["POST", "GET"])
async def sms_webhook(
    request: APIRequest, background_tasks: BackgroundTasks
) -> Response:
    if request.method == "GET":
        challenge = request.query_params.get("hub.challenge")
        return Response(
            content=challenge, status_code=200, headers={"Content-Type": "text/plain"}
        )

    body = await request.json()
    logger.debug("Received body:", body)
    text = whatsapp.get_text(body)
    media = whatsapp.get_media(body)
    phone = whatsapp.get_phone(body)

    if not phone:
        return None

    logger.debug(f"Text: {text}, Media: {media}, Phone: {phone}")

    latest_request = get_latest_request()
    started = False

    if latest_request is None or latest_request.started:
        logger.info("Starting new request")
        if text and text.lower() == "start":
            whatsapp.message_user(
                phone,
                "Welcome to the Marketplace Assistant! Please describe what you're looking for. "
                "You can also send images to help us find the best matches. When you're ready, type 'start' to begin.",
            )
        create_new_request(text, media)
    else:
        logger.info(f"Continuing current request {latest_request.id}")
        new_text = f"{latest_request.text}\n{text}" if text else latest_request.text
        updated_media = latest_request.media + media if media else latest_request.media
        if text.lower() == "start":
            started = True
        update_request_by_id(latest_request.id, new_text, updated_media, started)

    if started:
        logger.debug(f"Starting marketplace agent with prompt: {latest_request.text}")
        whatsapp.message_user(
            phone, "🫡 We're on it! We'll let you know when we find some matches."
        )
        background_tasks.add_task(start_shopping, phone, latest_request.text, media)
    else:
        whatsapp.message_user(
            phone,
            "Understood! Type 'start' when you're done providing instructions and we'll begin shopping.",
        )
    return None
