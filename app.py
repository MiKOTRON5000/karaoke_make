import os
import subprocess
import youtube_dl

ydl_opts = ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}

def download_video(url):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info)
    return video_file

def separate_audio(video_file, audio_file):
    subprocess.run(["ffmpeg", "-i", video_file, "-c:a", "libmp3lame", "-qscale:a", "1", audio_file])
    return audio_file

def separate_stems(audio_file, output_dir):
    subprocess.run(["python3", "-m", "spleeter", "separate", audio_file, "-o", output_dir, "-p", "spleeter:2stems"]) 

def create_lyrics_file(url):
    subprocess.run(["yt_whisper", url])
    for lyrics_file in os.listdir(os.getcwd()):
        if lyrics_file.endswith('.vtt'):
            print(lyrics_file)
            return lyrics_file       

def combine_video_accompaniment_lyrics(video_file, accompaniment_file, lyrics_file, output_file):
    subprocess.run(["ffmpeg", "-i", video_file, "-i", accompaniment_file, "-i", lyrics_file, "-map", "0:v", "-map", "1:a", "-map", "2", "-metadata:s:s:0", "language=eng", "-c:v", "copy", "-c:a", "aac", "-c:s", "mov_text", output_file])

def main():
    # Get video URL from user input
    url = input("Please enter the URL of the video you would like to download: ")
    
    # Create a file name for the video file, using the video's ID from the URL
    video_file = os.path.splitext(url.split("=")[-1])[0] + ".mp4"
    
    # Check if the video file already exists, if not download it
    if not os.path.exists(video_file):
        video_file = download_video(url)
    
    # Create a file name for the audio file, using the video file name
    audio_file = os.path.splitext(video_file)[0] + ".mp3"
    
    # Check if the audio file already exists, if not separate it from the video
    if not os.path.exists(audio_file):
        audio_file = separate_audio(video_file, audio_file)
    
    # Get the current working directory
    output_dir = os.getcwd()
    
    # Separate the audio into stems
    separate_stems(audio_file, output_dir)

    # Delete the unnecessary vocal.wav file
    os.remove(os.path.join(os.path.dirname(video_file), os.path.splitext(os.path.basename(video_file))[0], 'vocals.wav'))

    # Create a file name for the lyrics file, using the video's ID from the URL
    lyrics_file = create_lyrics_file(url)    
    
    # Create a file name for the final output video file, using the original video file name
    output_file = os.path.splitext(video_file)[0] + "_output.mp4"

    # Get the base file name of the audio file
    audio_file_base = os.path.splitext(os.path.basename(audio_file))[0]

    # Create a file name for the accompaniment file, using the audio file base name
    accompaniment_file = os.path.join(os.path.dirname(video_file), os.path.splitext(os.path.basename(video_file))[0], 'accompaniment.wav')
    
    # If accompaniment file not exist, use the audio_file_base
    if not accompaniment_file:
        accompaniment_file = os.path.join(audio_file_base, 'accompaniment.wav')

    # Get the directory path of accompaniment.wav
    directory_path = os.path.dirname(os.path.join(os.path.dirname(video_file), os.path.splitext(os.path.basename(video_file))[0], 'accompaniment.wav'))

    # Print the full path of the accompaniment file    
    print(os.path.abspath(accompaniment_file))
    
    # Delete the original audio file 
    os.remove(audio_file)
    
    # Combine the video, accompaniment, and lyrics files into the final output video file
    combine_video_accompaniment_lyrics(video_file, accompaniment_file, lyrics_file, output_file)

    # Delete the accompainiment file
    os.remove(os.path.join(os.path.dirname(video_file), os.path.splitext(os.path.basename(video_file))[0], 'accompaniment.wav')) 

    # Delete the accompainiment file's directory
    os.rmdir(directory_path)
    
    # Review the lyrics file
    subprocess.run(["less", lyrics_file])
    
    # Delete the lyrics file? 
    delete_file = input("Do you want to delete the lyrics file? (y/n) ")

    if delete_file.lower() in ("yes", "y"):
        os.remove(lyrics_file)    

    # Delete the original downloaded video?
    delete_file = input("Do you want to delete the original video? (y/n) ")

    if delete_file.lower() in ("yes", "y"):
        os.remove(video_file)

if __name__ == "__main__":
    main()