from moviepy.editor import *
from app.api.utils.audio import TTSProvider


def create_video(image_path, audio_path, output_path):
    try:
        # Load the image and audio

        image_clip = ImageClip(
            image_path, duration=TTSProvider.get_audio_duration(audio_path)
        )  # Change duration as needed
        audio_clip = AudioFileClip(audio_path)
        # Set the audio duration to match the image duration
        audio_clip = audio_clip.set_duration(image_clip.duration)
        # Set the audio to the image
        final_clip = image_clip.set_audio(audio_clip)
        # Write the video file
        final_clip.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=24
        )

    except Exception as e:
        print(f"An error occurred: {e}")
