# from pydub.generators import Sine

# import onnxruntime as ort
# import librosa  # For audio preprocessing (install librosa if not present)

# WAKE_WORD_ONNX_MODEL_PATH = "Ai_Models/WakeWords/hey_nukee.onnx"

# try:
#     ort_session = ort.InferenceSession(WAKE_WORD_ONNX_MODEL_PATH)
#     print_log("ONNX Wake Word model loaded successfully.")
# except Exception as e:
#     print_log(f"Failed to load ONNX Wake Word model: {e}")
#     exit(1)

# def preprocess_wake_word_audio(wav_path, target_sr=16000, n_mels=16, n_frames=96):
#     audio, sr = librosa.load(wav_path, sr=target_sr, mono=True)

#     n_fft = 400
#     hop_length = 160

#     mel_spec = librosa.feature.melspectrogram(
#         y=audio,
#         sr=sr,
#         n_fft=n_fft,
#         hop_length=hop_length,
#         n_mels=n_mels,
#         power=2.0  # Or 1.0 depending on model
#     )

#     log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)

#     if log_mel_spec.shape[1] < n_frames:
#         pad_width = n_frames - log_mel_spec.shape[1]
#         log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, pad_width)), mode='constant')
#     else:
#         log_mel_spec = log_mel_spec[:, :n_frames]

#     log_mel_spec = (log_mel_spec - log_mel_spec.min()) / (log_mel_spec.max() - log_mel_spec.min() + 1e-6)

#     input_tensor = np.expand_dims(log_mel_spec.astype(np.float32), axis=0)  # Shape: (1, 16, 96)

#     return input_tensor



# def wait_for_wake_word():
#     print_log(f"Waiting for wake word using ONNX model...")
#     print("Model input shape:", ort_session.get_inputs()[0].shape)

#     RATE = 16000
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1

#     p = pyaudio.PyAudio()
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#     frames = []
#     max_buffer_frames = int(RATE / CHUNK * 1)  # 1 second buffer
#     try:
#         while True:
#             data = stream.read(CHUNK, exception_on_overflow=False)
#             frames.append(data)

#             # Keep only last 1 second of audio
#             if len(frames) > max_buffer_frames:
#                 frames.pop(0)

#             # Save current frames to temp wav for model inference
#             if len(frames) == max_buffer_frames:
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
#                     path = tmpfile.name
#                 with wave.open(path, 'wb') as wf:
#                     wf.setnchannels(CHANNELS)
#                     wf.setsampwidth(p.get_sample_size(FORMAT))
#                     wf.setframerate(RATE)
#                     wf.writeframes(b''.join(frames))

#                 # Preprocess audio for model input
#                 input_audio = preprocess_wake_word_audio(path, target_sr=RATE)

#                 # Run ONNX model inference
#                 inputs = {ort_session.get_inputs()[0].name: input_audio}
#                 output = ort_session.run(None, inputs)
                
#                 score = output[0][0][1] if output[0].shape[-1] > 1 else output[0][0]

#                 # Convert to Python float if it's a numpy array
#                 if isinstance(score, np.ndarray):
#                     score = float(score.item())
#                 else:
#                     score = float(score)

#                 print_log(f"Wake word detection score: {score:.4f}")

#                 if score > 0.8:
#                     print_log("Wake word detected!")
#                     os.remove(path)
#                     break

#                 os.remove(path)
#     finally:
#         stream.stop_stream()
#         stream.close()
#         p.terminate()