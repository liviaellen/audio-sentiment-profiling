# Audio Emotion Analysis - Omi Plugin

A community plugin for Omi that provides real-time emotion analysis using Hume AI with automatic notifications.

## Features

- 🎤 Real-time audio streaming from Omi devices
- 🧠 Emotion analysis using Hume AI's Speech Prosody & Language models
- 📱 Automatic notifications via Omi app when emotions are detected
- 📊 Live dashboard with emotion statistics and percentages
- ⚙️ Configurable emotion thresholds

## Installation

### Option 1: Deploy to Render (Recommended)

1. Fork this repository
2. Click the "Deploy to Render" button
3. Set environment variables:
   - `HUME_API_KEY` - Your Hume AI API key
   - `OMI_APP_ID` - Your Omi app ID
   - `OMI_API_KEY` - Your Omi API key
4. Deploy and copy your app URL

### Option 2: Self-Host

```bash
# Clone repository
git clone <your-repo-url>
cd audio-sentiment-profiling

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python main.py
```

## Omi App Configuration

1. Open Omi mobile app
2. Go to **Settings** → **Developer Mode**
3. Under **"Realtime audio bytes"**, enter:
   ```
   https://your-app-name.onrender.com/audio
   ```
4. Enable the plugin in **Apps** section

## Configuration

Edit `emotion_config.json` to customize which emotions trigger notifications:

```json
{
  "notification_enabled": true,
  "emotion_thresholds": {
    "Joy": 0.5,
    "Anger": 0.6,
    "Sadness": 0.5
  },
  "notification_message_template": "🎭 Emotion Alert: Detected {emotions}"
}
```

**Empty thresholds = notify for ALL top 3 emotions!**

## API Endpoints

- `POST /audio` - Receives audio from Omi device
- `GET /` - Dashboard with emotion statistics
- `GET /status` - Server status (JSON)
- `POST /analyze-text` - Analyze emotion from text
- `GET /emotion-config` - View notification config
- `POST /emotion-config` - Update notification config
- `POST /reset-stats` - Reset statistics

## Requirements

- Python 3.11+
- Hume AI API key
- Omi device with app integration

## Support

For issues and questions, please open an issue on GitHub.

## License

MIT License
