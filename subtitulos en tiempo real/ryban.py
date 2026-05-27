import tkinter as tk
import threading
import queue
import sounddevice as sd
import vosk
import json
import numpy as np

# Configuración del modelo Vosk (descargar modelo español si no está)
MODEL_PATH = "model"

# Ventana de subtítulos
def create_subtitle_window(text_queue):
    root = tk.Tk()
    root.title('Subtítulos en tiempo real')
    label = tk.Label(root, text='', font=('Arial', 24), wraplength=800, justify='center')
    label.pack(padx=20, pady=40)

    def update_label():
        try:
            while True:
                text = text_queue.get_nowait()
                label.config(text=text)
        except queue.Empty:
            pass
        root.after(100, update_label)

    root.after(100, update_label)
    root.mainloop()

# Hilo de reconocimiento de voz
def recognize_audio(text_queue):
    if not vosk.Model or not hasattr(vosk, 'Model'):
        text_queue.put('Vosk no está correctamente instalado.')
        return
    try:
        model = vosk.Model(MODEL_PATH)
    except Exception:
        text_queue.put('Descarga el modelo de español de Vosk y colócalo en la carpeta "model".')
        return
    samplerate = 16000
    recognizer = vosk.KaldiRecognizer(model, samplerate)
    def callback(indata, frames, time, status):
        # Convertir el buffer a bytes de forma compatible
        try:
            audio_bytes = indata.tobytes()
        except AttributeError:
            audio_bytes = bytes(indata)
        if recognizer.AcceptWaveform(audio_bytes):
            result = recognizer.Result()
            text = json.loads(result).get('text', '')
            if text:
                text_queue.put(text)
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=callback):
        while True:
            sd.sleep(100)

if __name__ == '__main__':
    q = queue.Queue()
    t = threading.Thread(target=recognize_audio, args=(q,), daemon=True)
    t.start()
    create_subtitle_window(q)



















