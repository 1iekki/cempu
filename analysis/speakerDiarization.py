import torchaudio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from collections import defaultdict
import math

class SpeakerDiarization:
    def __init__(self):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token="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"
        )
    
    def run(self, audio_path, num_speakers=None):
        # Manual audio load
        waveform, sample_rate = torchaudio.load(audio_path)
        audio = {"waveform": waveform, "sample_rate": sample_rate}
        
        with ProgressHook() as hook:
            output = self.pipeline(audio, hook=hook, num_speakers=num_speakers)
        
        # Alternative
        # with ProgressHook() as hook:
        #     output = pipeline("audio.wav", hook=hook)  # runs locally

        return output
    
    def get_speaker_times(self, output):
        speaker_times = defaultdict(float)
        for segment, speaker in output.speaker_diarization:
            speaker_times[speaker] += segment.end - segment.start
        return dict(speaker_times)
    
    def engagement_score(self, speaker_times):
        speech_vector = [speaker_times[s] for s in sorted(speaker_times.keys())]
        num_speakers = len(speech_vector)
        total = sum(speech_vector)
        
        ideal = [total / num_speakers] * num_speakers
        dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(speech_vector, ideal)))
        
        max_vector = [total] + [0] * (num_speakers - 1)
        max_dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(max_vector, ideal)))
        
        engagement = 1 - (dist / max_dist)
        return engagement


if __name__ == "__main__":
    diarizer = SpeakerDiarization()
    
    output = diarizer.run("wavs/speaker_test.wav", num_speakers=5)
    
    # Speech segments
    for turn, speaker in output.speaker_diarization:
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
    
    speaker_times = diarizer.get_speaker_times(output)

    print("\nTotal speaking time:")
    for speaker in sorted(speaker_times.keys()):
        print(f"speaker_{speaker}: {speaker_times[speaker]:.2f} seconds")
    
    # Engagement calculation
    score = diarizer.engagement_score(speaker_times)
    print(f"\nEuclidean engagement: {score:.3f}")
