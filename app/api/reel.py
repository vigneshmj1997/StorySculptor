from openai import OpenAI
import json
import os
from tqdm import tqdm
from moviepy.editor import VideoFileClip, concatenate_videoclips
from app.api.utils.config import TEXT, IMAGE
from app.api.utils.image import DalleAzure
from app.api.utils.audio import AzureTTSProvider
from app.api.utils.video import create_video
from app.prompt import CREATE_STORY
from app.helper import generate_random_string
from static import STATIC_DIR


client = OpenAI()


class Reel:
    def __init__(self, story: str):
        self.story = story
        self.image_generator = DalleAzure()
        self.folder = str(generate_random_string())
        os.mkdir(os.path.join(STATIC_DIR, self.folder))
        os.mkdir(os.path.join(STATIC_DIR, self.folder, "Image"))
        os.mkdir(os.path.join(STATIC_DIR, self.folder, "Audio"))
        os.mkdir(os.path.join(STATIC_DIR, self.folder, "Video"))
        self.base_dir = os.path.join(STATIC_DIR, self.folder)
        self.audio_generator = AzureTTSProvider(
            config={
                "subscription_key": os.getenv("AZURE_SUBSCRIPTION_KEY"),
                "region": os.getenv("AZURE_REGION"),
            }
        )

    def create_chunks(self):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CREATE_STORY.render(story=self.story)}
            ],
        )
        try:
            self.chunks = json.loads(response.choices[0].message.content)
            print(self.chunks)
            return self.chunks
        except Exception as e:
            raise ValueError("The test cannot be converted to json Try again..!")

    def create_components(self):
        chunks = self.create_chunks()
        for idx, chunk in enumerate(chunks):
            IMAGE_PATH = os.path.join(self.base_dir, "Image", f"{idx}.png")
            AUDIO_PATH = os.path.join(self.base_dir, "Audio", f"{idx}.mp3")
            VIDEO_PATH = os.path.join(self.base_dir, "Video", f"{idx}.3gp")
            self.image_generator.generate_image(
                prompt=chunk[IMAGE], image_name=IMAGE_PATH, story=chunk[TEXT]
            )
            self.audio_generator.synthesize(
                text=chunk[TEXT], output_filename=AUDIO_PATH
            )
            create_video(
                image_path=IMAGE_PATH, audio_path=AUDIO_PATH, output_path=VIDEO_PATH
            )

    def make_reel(self):
        self.create_components()
        video_files = os.listdir(os.path.join(self.base_dir, "Video"))
        video_files.sort()
        loaded_video_list = []
        for video_file in tqdm(video_files):
            loaded_video_list.append(
                VideoFileClip(
                    os.path.join(os.path.join(self.base_dir, "Video"), video_file)
                )
            )
        final_clip = concatenate_videoclips(loaded_video_list)
        final_clip.write_videofile(
            os.path.join(self.base_dir, "Story.3gp"), codec="libx264", audio_codec="aac"
        )


if __name__ == "__main__":
    demo = Reel("temp")
    demo.make_reel()
