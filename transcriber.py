import requests
import colorama
import time
import os
import datetime
import sounddevice as sd
from scipy.io.wavfile import write
from colorama import Fore, Back
colorama.init(autoreset=True)


date = datetime.datetime.now().strftime("%h:%H:%M:%S")
transcript_txt = str(date).replace(":", "-") + ".txt"
transcript_audio = str(date).replace(":", "-") + ".wav"

folder = "Transcriptions"
save_path = os.path.join(folder, transcript_audio)

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

filename = save_path
headers = {'authorization': "YOUR API KEY"}

print()
input_option = input('''Audio file input (1)
Microphone input (2)
Enter option: ''')

print()
if input_option == "1":
    filename = str(input("Enter file name: "))


def audio_recording():
    print(Fore.YELLOW + "(●) Recording".center(100))

    frequency = 44100
    duration = 10
    record_audio = sd.rec(int(duration * frequency), samplerate=frequency, channels=2)
    sd.wait()
    write(save_path, frequency, record_audio)

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
    task_id = transcript_response.json()["id"]
    return task_id

def ask_api(transcript_id):
    ask_endpoint = transcript_endpoint + "/" + transcript_id
    ask_respone = requests.get(ask_endpoint, headers=headers)
    return ask_respone.json()

def transcribe_output(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        result = ask_api(transcript_id)
        if result["status"] == "completed":
            return result, None
        elif result["status"] == "error":
            return result, result["error"]
        
        # print("Waiting for 10 seconds...")
        # time.sleep(10)    

def save_transcript(audio_url):
    result, error = transcribe_output(audio_url)

    if result:
        text_file = save_path.replace(".wav", "") + ".txt"
        with open(text_file, "w") as f:
            f.write(result["text"])
        output = result["text"]
        print(output)
        print()
        print("Transcription saved")

    elif error:
        print()
        print("Transcription failed", error)


if input_option == "2":
    audio_recording()

audio_url = upload(filename)
save_transcript(audio_url)