import time
import pyperclip
import yt_dlp
import os
import threading
import queue

# --- Configuration ---
DOWNLOAD_FOLDER = "Downloads"
CHECK_INTERVAL = 0.5   # Checks clipboard every 0.5 seconds

# Create a queue to hold the URLs
url_queue = queue.Queue()

def download_worker():
    """
    Background task: waits for URLs in the queue and downloads them one by one.
    """
    while True:
        # 1. Get the next URL from the queue (blocks if empty)
        url = url_queue.get()
        
        print(f"\n[>>>] Processing: {url}")
        print(f"      (Items pending in queue: {url_queue.qsize()})")

        # 2. Ensure download folder exists
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        # 3. Original yt-dlp configuration
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': True,
        }

        # 4. Attempt download
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                print(f"[✓] Completed: {url}")
        except Exception as e:
            print(f"[!] Error processing {url}: {e}")
        finally:
            # Mark task as done so the queue updates
            url_queue.task_done()
            print("---------------------------------------------------")

def is_youtube_url(text):
    """Checks if the text looks like a YouTube URL."""
    return "youtube.com/watch" in text or "youtu.be/" in text

def monitor_clipboard():
    print("--- Queue-Based YouTube Downloader (Original Config) ---")
    print("1. Copy YouTube links continuously.")
    print("2. They will be added to the queue and downloaded one by one.")
    print("3. Press Ctrl+C to stop.")
    
    # Start the worker thread in the background
    # daemon=True means this thread will die when the main program exits
    threading.Thread(target=download_worker, daemon=True).start()
    
    last_text = pyperclip.paste()

    try:
        while True:
            current_text = pyperclip.paste()

            # Check if clipboard changed
            if current_text != last_text:
                last_text = current_text
                
                # If it's a YouTube link, add to Queue immediately
                if is_youtube_url(current_text):
                    print(f"\n[+] Added to Queue: {current_text}")
                    url_queue.put(current_text)
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[!] Script stopped by user.")

if __name__ == "__main__":
    monitor_clipboard()