from contextProcessor import ContextProcessor

def main():
    AUDIO_PATH = 'audio/pogil.wav'

    p = ContextProcessor()
    
    p.process(AUDIO_PATH)

if __name__ == "__main__":
    main()
