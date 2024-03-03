import base64
import json
from loguru import logger

from openai import OpenAI


class ImageRanker:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI()

    def images_to_base64(self, file_paths):
        base64_images = []
        for file_path in file_paths:
            with open(f"media/{file_path}.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(
                    image_file.read()).decode("utf-8")
                base64_images.append(encoded_string)
        return base64_images

    def construct_prompt(self, references, items=None, message=""):

        if items is None:
            items = []
        references_base64 = self.images_to_base64(references)

        message_array = [
            {
                "type": "text",
                "text": f"""The next {len(references)} images are the style I like and I'm looking to buy something in that style. """,
            },
            {
                "type": "text",
                "text": """
                You are a shopping assistant helping me with the following:
                {message}
                Return a ranked json list of the items.
                It should include the item name, index, rank, and whether I should buy it (be very discerning. I only want to buy stuff that fits my style).
                Do not include any other thinking or information before or after the json.
                The json format is:
                index: [item index]
                item_name: [string]
                rank: [item rank]
                buy: True/False
                """,
            },
        ]

        if len(references_base64) > 0:
            message_array.append(
                {
                    "type": "text",
                    "text": "Here are some additional images I've provided for inspiration",
                }
            )
            message_array.extend(
                [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{reference}",
                        },
                    }
                    for reference in references_base64
                ]
            )
        for index, item in enumerate(items[:5]):
            message_array.extend(
                (
                    {
                        "type": "text",
                        "text": f"The following item has an item_name of {item['product_name']} and has index {index}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": item["image_url"]},
                    },
                )
            )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{"role": "user", "content": message_array}],
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return {"error": str(e)}

    def convert_to_json(self, message):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "This message contains a list of JSON objects. Return a single JSON object containing a single key 'data' with the list of objects inside it",
                },
                {"role": "user", "content": message},
            ],
        )
        return json.loads(response.choices[0].message.content)

    def rank_images(self, reference_image_urls: list, items: list, message):
        try:

            response = self.construct_prompt(reference_image_urls, items)
            logger.debug(f"Ranker response: {response}")
            ranking = self.convert_to_json(response)
            return [items[i["index"]]["page_url"] for i in ranking["data"] if i["buy"]]
        except Exception as e:
            raise e
