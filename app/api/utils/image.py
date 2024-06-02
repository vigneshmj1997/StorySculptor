from openai import AzureOpenAI
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import json
from io import BytesIO


class DalleAzure:
    def __init__(self):
        self.client = AzureOpenAI(
            api_version="2024-02-01",
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        )

    def wrap_text(self, text: str, max_length: int) -> str:
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    def add_text_to_image(self, text, image, font_size=40):
        text = self.wrap_text(text, max_length=38)
        draw = ImageDraw.Draw(image)
        height_box = image.height // 16
        font = ImageFont.load_default(size=50)
        bbox = draw.textbbox([50, height_box * (13 - len(text.split("\n")))], text, font=font)
        draw.rectangle(bbox, fill="black")
        draw.text(
            [50, height_box * (13 - len(text.split("\n")))],
            text,
            font=font,
            fill=(255, 255, 255),
            align="center",
            stroke_width=1,
        )

        return image

    def generate_image(self, prompt, image_name, story):
        try:
            result = self.client.images.generate(
                model="dalle3",  # the name of your DALL-E 3 deployment
                prompt=prompt,
                n=1,
            )
            json_response = json.loads(result.model_dump_json())

            # Retrieve the generated image
            image_url = json_response["data"][0][
                "url"
            ]  # extract image URL from response
            generated_image = requests.get(image_url).content  # download the image

            # Convert to PIL Image
            image = self.add_text_to_image(
                text=story, image=Image.open(BytesIO(generated_image))
            )
            image.save(image_name)
        except Exception as e:
            raise ValueError(f"Error in generating image {e}")
