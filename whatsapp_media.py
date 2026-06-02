import os
import requests
import tempfile
import mimetypes

def get_media_url(media_id, token):
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_media(media_id, token):
    """
    Downloads media from WhatsApp and saves it to a temporary file.
    Returns the path to the downloaded file.
    """
    media_info = get_media_url(media_id, token)
    media_url = media_info.get("url")
    mime_type = media_info.get("mime_type", "image/jpeg")
    
    if not media_url:
        raise ValueError(f"Could not get URL for media_id {media_id}")
        
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(media_url, headers=headers, stream=True)
    response.raise_for_status()
    
    # Determine extension from mime_type
    ext = mimetypes.guess_extension(mime_type) or ".jpg"
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(temp_fd, 'wb') as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
            
    return temp_path
