import pyaudio
import wave
import queue
from volumeAnalysis import *
from cempuMQTT import *
import requests

SAMPLE_RATE = 48000
WINDOW_SIZE_IN_SEC = 10
CHUNK = SAMPLE_RATE * WINDOW_SIZE_IN_SEC

FORMAT = pyaudio.paInt16
CHANNELS = 1
WAVE_OUTPUT_FILENAME = "output.wav"
AUDIO_DEVICE_INDEX = 1

IP_ADDRESS = "192.168.0.7"

START_COMMAND = "START"
PAUSE_COMMAND = "PAUSE"
STOP_N_SEND_COMMAND = "STOP"

stop_flag = True
start_flag = False
pause_flag = False

audio_queue = queue.Queue()

p = pyaudio.PyAudio()

if p.is_format_supported(SAMPLE_RATE, input_device=AUDIO_DEVICE_INDEX, input_channels=CHANNELS, input_format=FORMAT): 
    print("Format Is Supported!!!") 
frames = []

def on_message_cempu(client, userdata, msg):
    global stop_flag
    global start_flag
    global pause_flag
    message = msg.payload.decode()
    if message == START_COMMAND and (stop_flag is True or pause_flag is True) and start_flag is False:
        stop_flag = False
        pause_flag = False
        start_flag = True
        print("STARTED")
    elif message == STOP_N_SEND_COMMAND and (start_flag is True or pause_flag is True) and stop_flag is False:
        start_flag = False
        pause_flag = False
        stop_flag = True
        print("STOPPED")
    elif message == PAUSE_COMMAND and start_flag is True and stop_flag is False and pause_flag is False:
        start_flag = False
        pause_flag = True
        stop_flag = False
        print("PAUSED")
    else:
        print(msg.topic, message)


def upload_file(file_path: str, server_url: str, timeout: int = 300):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(server_url, files = files, timeout = timeout)
            response.raise_for_status()
            print(response.status_code)
    except requests.exceptions.RequestException as e:
        print(e)

def processChunk(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

def record_audio():

    with CempuMQTT("dev1", callback=on_message_cempu) as mqtt:

        stream = p.open(format=FORMAT, input_device_index= AUDIO_DEVICE_INDEX,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=processChunk)

        print("* recording")

        while True:
            in_data = audio_queue.get()
            if pause_flag is False:
                frames.append(in_data)
                
                block = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                engagement = calculateEngagementFromWindow(block, SAMPLE_RATE)
                print(f"Engagement: {engagement}")
                mqtt.sendEngagement(engagement)

            if stop_flag is True:
                print("* Stopping recording")
                stream.stop_stream()
                stream.close()
                p.terminate()

                print(f"* Saving recording to {WAVE_OUTPUT_FILENAME}...")
                with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(b''.join(frames))
                
                print("* Done.")
                print("* Uploading the file to the server")
                upload_file(WAVE_OUTPUT_FILENAME, IP_ADDRESS)
                print("* Done uploading")
                break;
            
def main():
    while True:
        if start_flag is True:
            record_audio()

if __name__ == "__main__":
    main()