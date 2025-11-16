import soundfile as sf
import numpy as np

from scipy.signal import butter, sosfilt

def filterBlock(block, sample_rate, low=500, high=2500, ):
    sos = butter(4, [low, high], btype='band', fs=sample_rate, output='sos')
    return sosfilt(sos,block)

def printAudioProperties(stream: sf.SoundFile) -> None:
        print("Audio properties")
        print("Sample rate: ", stream.samplerate)
        print("Channels: ", stream.channels)
        print("Frames: ", stream.frames)
        print("Format: ", stream.format)


def main():

    WindowSizeInSec = 10
    BlockSize = 1 * 1024 #1kb

    with sf.SoundFile("lateralM.mp3") as stream:

        printAudioProperties(stream)

        blockBuffer = np.array([], dtype="float32")

        NumSamplesInWindow = WindowSizeInSec * stream.samplerate

        currentWindowStartInSec = 0

        for block in stream.blocks(blocksize=BlockSize, dtype='float32'):
            filteredBlock = filterBlock(block, stream.samplerate)
            blockBuffer = np.concatenate((blockBuffer,filteredBlock))

            if(len(blockBuffer) >= NumSamplesInWindow):
                window = blockBuffer[:NumSamplesInWindow]
                peaks = [np.max(np.abs(window[i:i+BlockSize])) for i in range(0, len(window), BlockSize)]

                peaks_db = 20 * np.log10(np.clip(peaks, 1e-12, None))

                stdPeak = np.std(peaks_db)
                print(f"{currentWindowStartInSec} - {currentWindowStartInSec + WindowSizeInSec}")
                print("std: ", stdPeak)

                blockBuffer = blockBuffer[NumSamplesInWindow:]
                currentWindowStartInSec += WindowSizeInSec



if __name__ == "__main__":
    main()
