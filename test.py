from utils import audio_processor
from core import transcriber
from core import summarizer

processor = audio_processor.process_input("https://youtu.be/qYNweeDHiyU")
transcription = transcriber.transcribe_all_chunks(processor, translate=False)
summary = summarizer.summarize(transcription)
title = summarizer.generate_title(transcription)
print("\nTitle:\n", title)
print("\nSummary:\n", summary)