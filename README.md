# Omi Audio Streaming Service with Hume AI (Python)

A Python FastAPI service to receive real-time audio streams from Omi DevKit devices, analyze emotions using Hume AI's Speech Prosody model, and store them as WAV files in Google Cloud Storage.

## Features

- Receives raw audio bytes from Omi devices via POST requests
- **Real-time emotion analysis** using Hume AI's Speech Prosody model
- Automatically generates WAV headers for audio data
- Uploads audio files to Google Cloud Storage
- Supports both DevKit1 (8kHz/16kHz) and DevKit2 (16kHz) sample rates
- Docker support for easy deployment
- Health check endpoint
- Returns detailed emotion predictions with timestamps

## Prerequisites

### Required
- Python 3.11+
- **Hume AI account and API key** ([Get one here](https://www.hume.ai/))

### Optional (for cloud storage)
- Google Cloud Platform account
- Google Cloud Storage bucket
- GCP service account with Storage Object Creator permissions

> **Note**: Google Cloud Storage is completely optional! You can use this service just for emotion analysis without storing files to GCS.

## Setup Options

Choose one of the setup methods below:

### Option A: Hume AI Only (No GCS) - Simplest!

Perfect if you just want emotion analysis without cloud storage.

**1. Get Your Hume AI API Key** (2 minutes)

1. Sign up at [Hume AI](https://www.hume.ai/)
2. Navigate to your dashboard
3. Create an API key
4. Copy your API key

**2. Set Environment Variables**

```bash
# Just set your Hume API key
export HUME_API_KEY=your_hume_api_key_here
```

**3. Install Dependencies**

```bash
# Install only core dependencies (skip GCS packages if you want)
pip install fastapi uvicorn[standard] hume
```

**4. Run the Server**

```bash
python main.py
```

**5. Configure Omi App**

Set endpoint: `https://your-url/audio?save_to_gcs=false`

That's it! Your audio will be analyzed but not stored.

---

### Option B: Hume AI + Google Cloud Storage - Full Features

Use this if you want both emotion analysis AND cloud storage.

### 1. Create a GCS Bucket

Follow the [Google Cloud Storage documentation](https://cloud.google.com/storage/docs/creating-buckets) to create a bucket.

### 2. Create Service Account Credentials

1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to **IAM & Admin > Service Accounts**
3. Create a new service account
4. Grant it the **Storage Object Creator** role
5. Create and download a JSON key file

### 3. Encode Credentials to Base64

```bash
# Linux/Mac
base64 -i your-credentials.json -o credentials-base64.txt

# Or use Python
python -c "import base64; print(base64.b64encode(open('your-credentials.json', 'rb').read()).decode())"
```

### 4. Get Your Hume AI API Key

1. Sign up at [Hume AI](https://www.hume.ai/)
2. Navigate to your dashboard
3. Create an API key
4. Copy your API key for the next step

### 5. Set Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
GOOGLE_APPLICATION_CREDENTIALS_JSON=<your_base64_encoded_credentials>
GCS_BUCKET_NAME=<your-bucket-name>
HUME_API_KEY=<your_hume_api_key>
```

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
# Make sure environment variables are set
export $(cat .env | xargs)

# Run the server
python main.py
```

The server will start on `http://localhost:8080`

### Test the Endpoint

```bash
# Health check
curl http://localhost:8080/health

# Test audio upload (with sample audio data)
curl -X POST "http://localhost:8080/audio?sample_rate=16000&uid=test-user-123" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@sample-audio.raw"
```

## Docker Deployment

### Build the Image

```bash
docker build -t omi-audio-streaming .
```

### Run the Container

```bash
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS_JSON="<base64_encoded_credentials>" \
  -e GCS_BUCKET_NAME="<your-bucket-name>" \
  -e HUME_API_KEY="<your_hume_api_key>" \
  omi-audio-streaming
```

## Cloud Deployment

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/omi-audio-streaming

# Deploy to Cloud Run
gcloud run deploy omi-audio-streaming \
  --image gcr.io/YOUR_PROJECT_ID/omi-audio-streaming \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS_JSON=<base64_credentials> \
  --set-env-vars GCS_BUCKET_NAME=<bucket-name> \
  --set-env-vars HUME_API_KEY=<your_hume_api_key>
```

### AWS/DigitalOcean/Other Platforms

Deploy using Docker. Make sure to:
1. Build the Docker image
2. Push to your container registry
3. Deploy with environment variables set
4. Expose port 8080

### Local Testing with Ngrok

```bash
# Install ngrok: https://ngrok.com/download

# Run your local server
python main.py

# In another terminal, expose it
ngrok http 8080
```

Use the ngrok URL as your endpoint in the Omi app.

## Configure Omi App

1. Open the Omi App on your device
2. Go to **Settings > Developer Mode**
3. Scroll to **Realtime audio bytes**
4. Set your endpoint: `https://your-domain.com/audio`
5. Set **Every x seconds** to your desired interval (e.g., 10)

## API Endpoints

### POST /audio

Receives audio bytes from Omi device, analyzes emotions with Hume AI, and optionally stores to GCS.

**Query Parameters:**
- `sample_rate` (required): Audio sample rate in Hz (8000 or 16000)
- `uid` (required): User unique ID
- `analyze_emotion` (optional): Whether to analyze with Hume AI (default: true)
- `save_to_gcs` (optional): Whether to save to Google Cloud Storage (default: true)

**Request Body:**
- Binary audio data (application/octet-stream)

**Usage Examples:**
- Emotion analysis only: `/audio?sample_rate=16000&uid=user123&save_to_gcs=false`
- Storage only: `/audio?sample_rate=16000&uid=user123&analyze_emotion=false`
- Both (default): `/audio?sample_rate=16000&uid=user123`

**Response:**
```json
{
  "message": "Audio processed successfully",
  "filename": "user123_20250102_143022_123456.wav",
  "gcs_path": "gs://your-bucket/user123_20250102_143022_123456.wav",
  "uid": "user123",
  "sample_rate": 16000,
  "data_size_bytes": 160000,
  "timestamp": "20250102_143022_123456",
  "hume_analysis": {
    "success": true,
    "total_predictions": 3,
    "predictions": [
      {
        "time": {
          "begin": 0.0,
          "end": 2.5
        },
        "emotions": [
          {"name": "Joy", "score": 0.85},
          {"name": "Excitement", "score": 0.72},
          {"name": "Calmness", "score": 0.45}
        ]
      }
    ]
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "omi-audio-streaming"
}
```

## Audio Format

- **Format:** WAV (PCM)
- **Channels:** Mono (1)
- **Bit Depth:** 16-bit
- **Sample Rate:** 8000 Hz (DevKit1 v1.0.2) or 16000 Hz (DevKit1 v1.0.4+, DevKit2)

## File Naming Convention

Audio files are saved with the following naming pattern:
```
{uid}_{timestamp}.wav
```

Example: `user123_20250102_143022_123456.wav`

## How It Works: Omi + Hume AI Integration

This service creates a seamless pipeline for real-time emotion analysis from Omi audio streams:

1. **Audio Capture**: Omi device captures audio and streams it to your endpoint
2. **WAV Conversion**: Raw audio bytes are converted to WAV format with proper headers
3. **Emotion Analysis**: Hume AI's Speech Prosody model analyzes the audio for emotional content
4. **Storage**: Audio file is uploaded to Google Cloud Storage
5. **Response**: Returns emotion predictions with timestamps and storage location

### Emotion Analysis Details

Hume AI's Speech Prosody model analyzes:
- **Vocal tone and pitch patterns**
- **Speech rhythm and tempo**
- **Energy and intensity**
- **Pause patterns**

The model can detect emotions like:
- Joy, Sadness, Anger, Fear, Surprise
- Excitement, Calmness, Anxiety, Confidence
- And many more nuanced emotional states

Each prediction includes:
- **Time range**: When in the audio the emotion was detected
- **Emotion scores**: Confidence scores (0-1) for each detected emotion
- **Multiple emotions**: Audio segments often contain multiple emotions simultaneously

### Use Cases

- **Mental health monitoring**: Track emotional patterns over time
- **Customer service**: Analyze caller emotions during support interactions
- **Voice journaling**: Detect emotional trends in personal recordings
- **Communication coaching**: Get feedback on emotional delivery in speech
- **Research**: Study emotional responses in various contexts

## Troubleshooting

### "GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set"

Make sure you've set the environment variable with your base64-encoded credentials.

### "Failed to decode credentials"

Ensure your credentials are properly base64-encoded and the JSON is valid.

### "GCS_BUCKET_NAME environment variable not set"

Set the `GCS_BUCKET_NAME` environment variable to your bucket name.

### "HUME_API_KEY environment variable not set"

Make sure you've set your Hume AI API key in the environment variables.

### Audio files not appearing in GCS

- Check your service account has the correct permissions
- Verify the bucket name is correct
- Check server logs for error messages

### No emotion analysis in response

- Verify your Hume API key is valid
- Check if `analyze_emotion=false` was passed in the query parameters
- Review server logs for Hume API errors
- Ensure the audio file is not corrupted or too short

### Hume API rate limits

Hume AI has rate limits on their API. If you're processing high volumes:
- Implement request queuing
- Add retry logic with exponential backoff
- Consider caching results for duplicate audio

## License

MIT

## Contributing

Feel free to open issues or submit pull requests!

## Acknowledgments

- [Omi](https://www.omi.me/) - For the amazing wearable AI device
- [Hume AI](https://www.hume.ai/) - For the powerful emotion analysis API
- [Google Cloud Platform](https://cloud.google.com/) - For reliable storage
