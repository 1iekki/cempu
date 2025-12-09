import numpy as np
from scipy.signal import butter, sosfilt

def filterBlock(block, sample_rate, low=500, high=2500):
    sos = butter(4, [low, high], btype='band', fs=sample_rate, output='sos')
    return sosfilt(sos,block)

def normalize(x, lowerBound, upperBound):
     if x <= lowerBound:
          return 0.0
     if x >= upperBound:
          return 1.0
     
     return (x - lowerBound) / (upperBound - lowerBound)

def calculateEngagementFromWindow(block, sampleRate):

    analysisBlockSize = 1 * 1024 #1kb

    block = filterBlock(block, sampleRate)

    peaks = [np.max(np.abs(block[i:i+analysisBlockSize])) for i in range(0, len(block), analysisBlockSize)]
    peaksInDB = 20 * np.log10(np.clip(peaks, 1e-12, None))

    stdPeak = np.std(peaksInDB)

    STDLowerBound = 7
    STDHighBound = 13

    engagement = normalize(stdPeak, STDLowerBound, STDHighBound) * 100

    return engagement
     

def main():
    import soundfile as sf
    def printAudioProperties(stream: sf.SoundFile) -> None:
        print("Audio properties")
        print("Name: ", stream.name)
        print("Sample rate: ", stream.samplerate)
        print("Channels: ", stream.channels)
        print("Frames: ", stream.frames)
        print("Format: ", stream.format)

    WindowSizeInSec = 10
    BlockSize = 1 * 1024 #1kb

    STDLowerBound = 7
    STDHighBound = 13

    with sf.SoundFile("audio/pogil.wav") as stream:

        printAudioProperties(stream)

        blockBuffer = np.array([], dtype="float32")

        engagementValues = []

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

                engagement = normalize(stdPeak, STDLowerBound, STDHighBound) * 100
                print("Predicted engagement level: ", engagement)

                engagementValues.append(engagement)

                blockBuffer = blockBuffer[NumSamplesInWindow:]
                currentWindowStartInSec += WindowSizeInSec

        
        engagementArray = np.array(engagementValues)
        print("Average engagement: ", engagementArray.mean())



if __name__ == "__main__":
    main()
