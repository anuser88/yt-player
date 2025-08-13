import cv2
import threading
import time
import yt_dlp
import os
import psutil
import subprocess
import sys
class Audio:
    def __init__(self,proc):
        self.audiotstamp=time.time()
        self.audiottemp=0
        self.running=True
        self.proc=proc
    def getaudiotime(self):
        return time.time()-self.audiotstamp if self.running else self.audiottemp
    def pause(self):
        if self.running:
            self.audiottemp=self.getaudiotime()
            self.running=False
            self.proc.suspend()
    def resume(self):
        if not selfrunning:
            self.audiotstamp=time.time()-self.audiottemp
            self.running=True
            self.proc.resume()

def video(url, tmp_path):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
    # Play with ffplay (from FFmpeg)
    proc=subprocess.Popen([
        "ffplay", "-nodisp", "-autoexit", audio_url
    ])
    t=Audio(psutil.Process(proc.pid))
    r=threading.Thread(target=play_video_while_downloading, args=(tmp_path+"video.mp4",t,))
    r.start()

def download_video(url, output):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def cleanup(path):
    os.system(f"rd {path} /s /q")

def play_video_while_downloading(video_file,audioctrl):
    cap = cv2.VideoCapture(video_file)
    last_frame_count = 0
    window_ready = False
    while True:
        ret, frame = cap.read()
        if ret:
            if not window_ready:
                window_ready = True
            cv2.imshow('Streaming Video', frame)
            last_frame_count += 1
            if cv2.waitKey(30) & 0xFF == ord('q'):
                cleanup('yt-temp\\')
                break
            pos = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            if abs(pos-audioctrl.getaudiotime())>0.1:
                cap.set(cv2.CAP_PROP_POS_MSEC, audioctrl.getaudiotime()*1000)
        else:
            # No new frame - wait and retry (file might be still downloading)
            stuck=time.time()
            audioctrl.pause()
            while time.time()-stuck < 5:
                if ret:
                    audioctrl.resume()
                    stuck="pass"
                    print(12345)
                    break
            print(67890)
            if stuck != "pass":
                break
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

# Run download in background
def ytplay(video_url):
    output_path = 'yt-temp\\'
    d1 = threading.Thread(target=download_video, args=(video_url, output_path+"video.mp4"))
    d2 = threading.Thread(target=video, args=(video_url,output_path,))
    d1.start()
    d2.start()
    d1.join()
    d2.join()

if __name__ == "__main__":
    ytplay('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
