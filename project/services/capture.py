import cv2
import yt_dlp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def capture_youtube_frame(youtube_url: str, output_path: str = "camera_frame.jpg") -> str:
    """
    Extracts the direct stream URL from YouTube, reads a single frame using OpenCV, 
    and saves it to the disk.
    """
    # Options for yt-dlp: get the best video quality, no audio, no playlists
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]/best',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        logger.info(f"[*] Extracting stream URL for: {youtube_url}")
        # Step 1: Extract the raw video stream URL without downloading the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            stream_url = info_dict.get('url')
            
        if not stream_url:
            logging.error("[-] Error: Could not extract stream URL.")
            return False

        logger.info("[+] Stream URL extracted successfully. Connecting via OpenCV...")

        # Step 2: Connect to the stream and capture a frame
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            logger.error("[-] Error: Failed to open the video stream.")
            return False

        # Read a single frame
        ret, frame = cap.read()
        
        if ret:
            # Save the frame to a file
            cv2.imwrite(output_path, frame)
            logger.info(f"[+] Successfully saved frame to: {output_path}")
            success = True
        else:
            logger.error("[-] Error: Failed to read frame from stream.")
            success = False

    except Exception as e:
        logger.error(f"[-] An exception occurred: {e}")
        success = False

    finally:
        # Step 3: Cleanup - Release resources (crucial to avoid memory leaks)
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            logger.info("[*] Video capture resources released.")

    return success

# --- Test the script ---
if __name__ == "__main__":
    # Test URL (Replace with your actual YouTube live stream URL)
    test_url = "https://www.youtube.com/watch?v=DjdUEyjx8GM" 
    
    logging.info("Starting capture process...")
    capture_youtube_frame(test_url)
    logging.info("Process finished.")