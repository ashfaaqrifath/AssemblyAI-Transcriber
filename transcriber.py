import requests
import colorama
import time
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from colorama import Fore, Back
colorama.init(autoreset=True)


upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
#filename = "Recording.wav"
save_pathB = "record.wav"
filename = save_pathB
headers = {'authorization': "YOUR API KEY"}


def audio_recording():
    print(Fore.YELLOW + "(●) Recording".center(100))

    frequency = 44100
    duration = 10
    record_audio = sd.rec(int(duration * frequency), samplerate=frequency, channels=2)
    sd.wait()
    write(save_pathB, frequency, record_audio)

    print(Fore.GREEN + "Recoding audio completed".center(100))



def upload(filename):
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(filename))

    audio_url = upload_response.json()["upload_url"]
    return audio_url



def transcribe(audio_url):
    transcript_request = {"audio_url": audio_url}
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    job_id = transcript_response.json()["id"]
    return job_id



def poll(transcript_id):
    polling_endpoint = transcript_endpoint + "/" + transcript_id
    polling_respone = requests.get(polling_endpoint, headers=headers)
    return polling_respone.json()

def result_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        if data["status"] == "completed":
            return data, None
        elif data["status"] == "error":
            return data, data["error"]
        
        # print("Waiting for 10 seconds...")
        # time.sleep(10)
        

def save_transcript(audio_url):
    data, error = result_url(audio_url)

    if data:
        text_file = filename + ".txt"
        with open(text_file, "w") as f:
            f.write(data["text"])

        output = data["text"]
        print(output)

        print()
        print("Transcription saved")

    elif error:
        print()
        print("Transcription failed", error)



audio_recording()
audio_url = upload(filename)
save_transcript(audio_url)