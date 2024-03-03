from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi import Request as APIRequest
from loguru import logger  # noqa

import api.whatsapp as whatsapp
from api.db import create_new_request, get_latest_request, update_request_by_id
from api.facebook_marketplace_scraper import FacebookMarketplaceScraper
from api.image_ranker import ImageRanker
from api.multion import MarketplaceAssistant
from api.utils import list_to_str, str_to_list

app = FastAPI()


async def scrape_marketplace(prompt: str, search_url: str, media: List[str]) -> List[str]:
    scraper = FacebookMarketplaceScraper(headless=False)
    items = await scraper.scrape(search_url)
    try:
        # Initialize the ranker
        ranker = ImageRanker()
        return ranker.rank_images(media, items, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


async def start_shopping(
    phone: str, prompt: str, media: Optional[List[str]] = None
) -> None:
    media = media or []
    agent = MarketplaceAssistant()
    filter_res = await agent.filter(prompt)
    if search_url := filter_res.get("url"):
        product_urls = await scrape_marketplace(prompt, search_url, media)
        for url in product_urls:
            try:
                await agent.message_seller(url)
                whatsapp.message_user(phone, [url])
            except Exception as e:
                logger.exception(f"Error messaging seller for URL {url}. {e}")
    logger.debug(
        f"Marketplace assistant did not return valid URL {filter_res}")


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
                "You must describe what you're looking for and (optionally) provide images before we can start shopping.",
            )
        create_new_request(text, list_to_str(media))
    else:
        logger.info(f"Continuing current request {latest_request.id}")
        updated_text = latest_request.text
        updated_media = list_to_str(str_to_list(
            latest_request.media) + media) if media else latest_request.media
        if text.lower() == "start":
            if not latest_request.text:
                whatsapp.message_user(
                    phone, "You must describe what you're looking for before we can start shopping.",)
            else:
                started = True
        elif updated_text and text:
            updated_text = updated_text + "\n" + text
        elif text:
            updated_text = text
        update_request_by_id(latest_request.id, updated_text,
                             updated_media, started)

    if started:
        logger.debug(
            f"Starting marketplace agent with prompt: {latest_request.text}")
        whatsapp.message_user(
            phone, "🫡 We're on it! We'll let you know when we find some matches."
        )
        background_tasks.add_task(
            start_shopping, phone, latest_request.text, updated_media)
    else:
        whatsapp.message_user(
            phone,
            "Understood! Type 'start' when you're done providing instructions and we'll begin shopping.",
        )
    return None
