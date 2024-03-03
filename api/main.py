from fastapi import FastAPI


from api.perception import MarketplaceAssistant

app = FastAPI()


@app.get("/")
async def hello():
    return {"message": "Hello World"}


@app.put("/query")
async def query(prompt: str):
    """
    Endpoint to handle queries to the MarketplaceAssistant.

    :param prompt: The query string to be used for searching the marketplace.
    :return: A JSON list of matching marketplace items.
    """
    agent = MarketplaceAssistant()
    return await agent.query(prompt)
