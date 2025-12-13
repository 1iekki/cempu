import pyaudio
import wave
import queue
from volumeAnalysis import *
from cempuMQTT import *

SAMPLE_RATE = 48000
WINDOW_SIZE_IN_SEC = 10
CHUNK = SAMPLE_RATE * WINDOW_SIZE_IN_SEC

FORMAT = pyaudio.paInt16
CHANNELS = 1
WAVE_OUTPUT_FILENAME = "output.wav"
AUDIO_DEVICE_INDEX = 1

audio_queue = queue.Queue()

p = pyaudio.PyAudio()

if p.is_format_supported(SAMPLE_RATE, input_device=AUDIO_DEVICE_INDEX, input_channels=CHANNELS, input_format=FORMAT): 
    print("Format Is Supported!!!") 
frames = []

def processChunk(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

def main():

    with CempuMQTT("dev1") as mqtt:

        stream = p.open(format=FORMAT, input_device_index= AUDIO_DEVICE_INDEX,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=processChunk)

        print("* recording")

        try:
            while True:
                in_data = audio_queue.get()
                frames.append(in_data)
                
                block = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                engagement = calculateEngagementFromWindow(block, SAMPLE_RATE)
                print(f"Engagement: {engagement}")
                mqtt.sendEngagement(engagement)

        except KeyboardInterrupt:
            print("\n* Stopping recording...")
        
        finally:
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

if __name__ == "__main__":
    main()