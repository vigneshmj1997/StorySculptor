import os
import azure.cognitiveservices.speech as speechsdk
from google.cloud import texttospeech
import boto3
import random
import string
from botocore.exceptions import BotoCoreError, ClientError


class TTSProvider:
    def __init__(self, config):
        self.config = config

    def synthesize(self, text, output_filename):
        raise NotImplementedError("Subclasses must implement synthesize method")


class AzureTTSProvider(TTSProvider):

    def __init__(self, config):
        super().__init__(config)
        self.speech_config = speechsdk.SpeechConfig(
            subscription=config["subscription_key"], region=config["region"]
        )

    def synthesize(self, text, output_filename):
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(
                f"Azure TTS: Speech synthesized for text [{text}] and saved to [{output_filename}]"
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(
                f"Azure TTS: Speech synthesis canceled: {cancellation_details.reason}"
            )
            if (
                cancellation_details.reason == speechsdk.CancellationReason.Error
                and cancellation_details.error_details
            ):
                print(f"Azure TTS: Error details: {cancellation_details.error_details}")


class GoogleTTSProvider(TTSProvider):
    def __init__(self, config):
        super().__init__(config)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["credentials_json"]
        self.client = texttospeech.TextToSpeechClient()

    def synthesize(self, text, output_filename):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(
                f"Google TTS: Speech synthesized for text [{text}] and saved to [{output_filename}]"
            )


class AWSTTSProvider(TTSProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = boto3.Session(
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
            region_name=config["region"],
        ).client("polly")

    def synthesize(self, text, output_filename):
        try:
            response = self.client.synthesize_speech(
                Text=text, OutputFormat="pcm", VoiceId="Joanna"
            )

            with open(output_filename, "wb") as out:
                out.write(response["AudioStream"].read())
                print(
                    f"Amazon Polly: Speech synthesized for text [{text}] and saved to [{output_filename}]"
                )
        except (BotoCoreError, ClientError) as error:
            print(f"Amazon Polly: The service returned an error: {error}")


def generate_random_string(length=15):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string
