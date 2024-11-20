# client_app/request_content.py
import requests

def request_content(surrogate_server_url, content_id, save_path='downloaded_content'):
    """
    Request content from the Surrogate Server and save it locally.
    """
    try:
        response = requests.get(f"{surrogate_server_url}/content/{content_id}", stream=True)
        if response.status_code == 200:
            # Extract filename from headers if available
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = save_path
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Content '{content_id}' downloaded successfully as '{filename}'.")
        else:
            print(f"Error: {response.json().get('error')}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    SURROGATE_SERVER_URL = 'http://localhost:5001'  # Surrogate Server URL
    CONTENT_ID = 'sample_video.mp4'  # Content ID to request
    request_content(SURROGATE_SERVER_URL, CONTENT_ID)
