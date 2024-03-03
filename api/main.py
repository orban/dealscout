from fastapi import FastAPI, HTTPException, UploadFile, File
from .image_ranker import ImageRanker
from typing import List
from .facebook_marketplace_scraper import FacebookMarketplaceScraper

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