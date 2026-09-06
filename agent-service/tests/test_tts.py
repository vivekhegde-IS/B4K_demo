from kokoro_onnx import Kokoro
import soundfile as sf
import os

print("Loading Kokoro...")

kokoro = Kokoro(
    "kokoro-v1.0.onnx",
    "voices-v1.0.bin"
)

print("Kokoro loaded successfully!")

text = "नमस्कार दोस्तों, मेरा नाम कौस्तुभ है। मैं अभी बीमार हूँ। मेरा काम क्या है, कोई बोलो?"

print("Generating Hindi speech...")

samples, sample_rate = kokoro.create(
    text,
    voice="hf_alpha",
    speed=1.0,
    lang="hi"
)

sf.write("hindi_output.wav", samples, sample_rate)

print("Hindi audio generated: hindi_output.wav")

os.startfile("hindi_output.wav")