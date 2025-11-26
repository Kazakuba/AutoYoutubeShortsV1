import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.utils import get_base_dir, get_latest_video_data

def authenticate_youtube():
    base_dir = get_base_dir()
    client_secrets = os.path.join(base_dir, "config", "client_secrets.json") 
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def upload_video():
    base_dir = get_base_dir()
    title, data = get_latest_video_data()
    
    if not title:
        return

    video_path = os.path.join(base_dir, data.get("final_video", ""))
    if not os.path.exists(video_path):
        return

    youtube = authenticate_youtube()
    
    body = {
        "snippet": {
            "title": title.replace("_", " "),
            "description": f"AI generated video on {data['topic']}",
            "tags": ["AI", "Shorts"],
            "categoryId": "28"
        },
        "status": {
            "privacyStatus": "public", 
            "selfDeclaredMadeForKids": False
        }
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    response = request.execute()
    print(f"Uploaded: https://www.youtube.com/watch?v={response['id']}")