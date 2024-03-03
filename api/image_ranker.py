import json
from typing import List, Dict, Any

from openai import OpenAI
import os


class ImageRanker:
    def __init__(self) -> None:
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def construct_prompt(
        self, references: List[str], items: List[Dict[str, Any]]
    ) -> str:
        message_array = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"""The next {len(references)} images are the style I like and I'm looking to buy something in that style.
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
            }
        ]

        for reference in references:
            message_array.extend(
                [
                    {
                        "role": "user",
                        "content": {
                            "type": "image_url",
                            "image_url": {"url": reference},
                        },
                    },
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": "The following images are items I'm considering buying.",
                        },
                    },
                ]
            )

        for index, item in enumerate(items[:5]):
            message_array.extend(
                [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"The following item has an item_name of {item['product_name']} and has index {index}",
                        },
                    },
                    {
                        "role": "user",
                        "content": {
                            "type": "image_url",
                            "image_url": {"url": item["image_url"]},
                        },
                    },
                ]
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=message_array,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({"error": str(e)})

    def convert_to_json(self, message: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "parse this message and extract the json from it",
                    },
                    {"role": "user", "content": message},
                ],
            )
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}") from e

    def rank_images(
        self, reference_image_urls: List[str], items: List[Dict[str, Any]]
    ) -> List[str]:
        response = self.construct_prompt(reference_image_urls, items)
        ranking = self.convert_to_json(response)
        return [items[i["index"]]["page_url"] for i in ranking["data"] if i["buy"]]
