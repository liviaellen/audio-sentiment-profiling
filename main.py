import os
import base64
import json
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import storage
from google.oauth2 import service_account
from hume import AsyncHumeClient
from hume.expression_measurement.stream import Config
from hume.expression_measurement.stream.socket_client import StreamConnectOptions
from hume.expression_measurement.stream.types import StreamProsody
import uvicorn

app = FastAPI(title="Omi Audio Streaming Service with Hume AI")


def create_wav_header(sample_rate: int, data_size: int) -> bytes:
    """
    Create a WAV file header for the audio data.

    Args:
        sample_rate: Audio sample rate in Hz (typically 8000 or 16000)
        data_size: Size of the audio data in bytes

    Returns:
        44-byte WAV header
    """
    num_channels = 1  # Mono
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8

    # RIFF header
    header = bytearray()
    header.extend(b'RIFF')
    header.extend((36 + data_size).to_bytes(4, 'little'))
    header.extend(b'WAVE')

    # fmt subchunk
    header.extend(b'fmt ')
    header.extend((16).to_bytes(4, 'little'))  # Subchunk size
    header.extend((1).to_bytes(2, 'little'))   # Audio format (PCM)
    header.extend(num_channels.to_bytes(2, 'little'))
    header.extend(sample_rate.to_bytes(4, 'little'))
    header.extend(byte_rate.to_bytes(4, 'little'))
    header.extend(block_align.to_bytes(2, 'little'))
    header.extend(bits_per_sample.to_bytes(2, 'little'))

    # data subchunk
    header.extend(b'data')
    header.extend(data_size.to_bytes(4, 'little'))

    return bytes(header)


def upload_to_gcs(file_path: str, bucket_name: str, destination_blob_name: str) -> str:
    """
    Upload a file to Google Cloud Storage.

    Args:
        file_path: Path to the local file
        bucket_name: GCS bucket name
        destination_blob_name: Name for the blob in GCS

    Returns:
        Public URL of the uploaded file
    """
    # Get credentials from environment variable
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set")

    # Decode base64 credentials
    try:
        credentials_dict = json.loads(base64.b64decode(credentials_json))
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    except Exception as e:
        raise ValueError(f"Failed to decode credentials: {e}")

    # Create GCS client
    client = storage.Client(credentials=credentials, project=credentials_dict.get('project_id'))
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload file
    blob.upload_from_filename(file_path, content_type='audio/wav')

    return f"gs://{bucket_name}/{destination_blob_name}"


async def analyze_audio_with_hume(wav_file_path: str) -> Dict[str, Any]:
    """
    Analyze audio file with Hume AI Speech Prosody model.

    Args:
        wav_file_path: Path to the WAV audio file

    Returns:
        Dict containing emotion predictions from Hume AI
    """
    hume_api_key = os.getenv('HUME_API_KEY')
    if not hume_api_key:
        raise ValueError("HUME_API_KEY environment variable not set")

    try:
        client = AsyncHumeClient(api_key=hume_api_key)
        model_config = Config(prosody=StreamProsody())
        stream_options = StreamConnectOptions(config=model_config)

        async with client.expression_measurement.stream.connect(options=stream_options) as socket:
            result = await socket.send_file(wav_file_path)

            # Extract prosody predictions
            if result and hasattr(result, 'prosody') and result.prosody:
                predictions = result.prosody.predictions

                # Format the results
                formatted_results = []
                for prediction in predictions:
                    pred_data = {
                        "time": {
                            "begin": prediction.time.begin if hasattr(prediction.time, 'begin') else None,
                            "end": prediction.time.end if hasattr(prediction.time, 'end') else None
                        },
                        "emotions": [
                            {"name": emotion.name, "score": emotion.score}
                            for emotion in prediction.emotions
                        ]
                    }
                    formatted_results.append(pred_data)

                return {
                    "success": True,
                    "predictions": formatted_results,
                    "total_predictions": len(formatted_results)
                }
            else:
                return {
                    "success": False,
                    "error": "No prosody predictions returned",
                    "predictions": []
                }
    except Exception as e:
        print(f"Error analyzing audio with Hume: {e}")
        return {
            "success": False,
            "error": str(e),
            "predictions": []
        }


@app.post("/audio")
async def handle_audio_stream(
    request: Request,
    sample_rate: int = Query(..., description="Audio sample rate in Hz"),
    uid: str = Query(..., description="User ID"),
    analyze_emotion: bool = Query(True, description="Whether to analyze emotions with Hume AI"),
    save_to_gcs: bool = Query(True, description="Whether to save audio to Google Cloud Storage")
):
    """
    Endpoint to receive audio bytes from Omi device, optionally analyze with Hume AI and/or save to GCS.

    Query Parameters:
        - sample_rate: Audio sample rate (e.g., 8000 or 16000)
        - uid: User unique ID
        - analyze_emotion: Whether to analyze emotions with Hume AI (default: True)
        - save_to_gcs: Whether to save audio to GCS (default: True)

    Body:
        - Binary audio data (application/octet-stream)
    """
    try:
        # Read audio bytes from request body
        audio_data = await request.body()

        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data received")

        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{uid}_{timestamp}.wav"

        # Create WAV header
        wav_header = create_wav_header(sample_rate, len(audio_data))

        # Combine header and audio data
        wav_data = wav_header + audio_data

        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(wav_data)
            temp_file_path = temp_file.name

        try:
            # Analyze with Hume AI if requested
            hume_results = None
            if analyze_emotion:
                print(f"Analyzing audio with Hume AI for user {uid}")
                hume_results = await analyze_audio_with_hume(temp_file_path)
                print(f"Hume analysis complete: {hume_results.get('total_predictions', 0)} predictions")

            # Upload to GCS if requested
            gcs_path = None
            if save_to_gcs:
                bucket_name = os.getenv('GCS_BUCKET_NAME')
                if not bucket_name:
                    print("Warning: GCS_BUCKET_NAME not set, skipping GCS upload")
                else:
                    try:
                        gcs_path = upload_to_gcs(temp_file_path, bucket_name, filename)
                        print(f"Audio file uploaded successfully: {gcs_path}")
                    except Exception as e:
                        print(f"Warning: Failed to upload to GCS: {e}")
                        # Continue processing even if GCS upload fails

            response_data = {
                "message": "Audio processed successfully",
                "filename": filename,
                "uid": uid,
                "sample_rate": sample_rate,
                "data_size_bytes": len(audio_data),
                "timestamp": timestamp
            }

            # Add GCS path if available
            if gcs_path:
                response_data["gcs_path"] = gcs_path

            # Add Hume results if available
            if hume_results:
                response_data["hume_analysis"] = hume_results

            return JSONResponse(
                status_code=200,
                content=response_data
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "omi-audio-streaming"}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8080)
