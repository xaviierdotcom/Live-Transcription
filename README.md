# Speech Recognition App

Simple desktop application I built for live transcription of speech. Great for meetings, lectures, or when you need live subtitles!

## What it does

- **Live speech-to-text** - Transcribes your speech into text in real time
- **Auto-typing** - Can automatically type out the transcribed text (so handy!)
- **Device selection** - Select any microphone you like
- **Clean interface** - Simple, no-frills design
- **Timestamped text** - Look exactly when you said what

## Getting started

### What you need

- Python 3.8+ (use 3.10 or above, I suggest)
- A microphone (the one built-in or an external one)
- Around 4GB of free RAM
- Internet on the first run (downloads the AI model)

### Installation

1. **Download the files** or clone this repository
2. **Create a virtual environment** (listen to me, do this):
   ```bash
   python -m venv speech_env
```
# Windows:
   speech_env\Scripts\activate
   # Mac/Linux:
   source speech_env/bin/activate
   ```

3. **Install everything**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (the app needs this):
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

### Run it

```bash
python app.py
```

That's it! The first time will be lengthy as it downloads the AI model (~3GB).

## How to use

1. Choose your microphone from the dropdown
2. Turn on "Enable Auto-Typing" if you want it to type for you
3. Click "Start" and speak
4. Watch your words appear with timestamps
5. Click "Stop" when finished

### Pro tips

- **Speak loudly** - the AI is good but not magic
- **Quiet setting** makes a big difference
- **Good microphone** = better outcome
- **GPU highly recommended** - it will be 5-10x faster

## Speeding it up (GPU configuration)

If you've got an NVIDIA graphics card, it can speed this up a lot:

```bash
# Check if you have CUDA support
python -c "import torch; print(torch.cuda.is_available())"

# If it prints False, install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

You will also need CUDA installed on your system. Check on NVIDIA's website for the latest one.

## Troubleshooting

**"No microphones found"**
- Make sure your mic is plugged and working
- Try another mic
- Restart the app

**"Missing dependency" errors**
- Make sure you're in your virtual environment
- Run: `pip install -r requirements.txt` again

**App is really slow**
- First run always takes a while (downloading the model)
- Without GPU it's slower but should work
- Shut down other programs that use your microphone

**Auto-typing not working**
- Certain apps prevent automated typing
- Try a text editor first, something basic
- On Mac, you might have to grant permission in System Preferences

## What's under the hood

- **Faster-Whisper** - The AI speech-to-text
- **RealtimeSTT** - Handles the real-time audio
- **Tkinter** - The GUI library (included in Python)
- **PyTorch** - Runs the AI model
- **Various other libraries** - Audio processing, keyboard automation, etc.

## A few notes

This is my own personal project because I needed live captions on video calls. It works for me, but your mileage will differ depending on your hardware.

The voice recognition is excellent - it is based on the cutting-edge OpenAI's Whisper model. It handles accents, background noise, and several languages quite well.

Performance is very hardware-dependent. With a decent GPU it's virtually instantaneous. On CPU-only slower but still functional.

## Issues?

If things don't work:

1. Make sure all the requirements are installed
2. Make sure microphone permissions are set correctly
3. Try using a different microphone
4. Check the console for error messages

---

**Let's go!** Just type `python app.py` and start talking!
