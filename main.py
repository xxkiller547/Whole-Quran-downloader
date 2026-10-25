#==================================================================================================
import requests
from pathlib import Path
from moviepy.editor import AudioFileClip, concatenate_audioclips
#==================================================================================================
BASE_DIR =Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
RECITERS_API_URL = "https://www.mp3quran.net/api/v3/reciters?language=eng"
#==================================================================================================
def DownloadWholeQuran():
    response = requests.get(RECITERS_API_URL)

    if response.status_code != 200:
        print("Failed to fetch reciters data")

    reciters = response.json()["reciters"]

    print("Available Reciters:")
    for index, reciter in enumerate(reciters, start=1):
        print(f" - {index}. {reciter['name']}")

    while True:
        try:
            user_input = input("Select a reciter by number: ")
            index = int(user_input) - 1
            if index < 0 or index >= len(reciters): 
                print("Invalid input. Please select a valid reciter.")
                continue
            break
        except (ValueError, IndexError):
            print("Invalid input. Please select a valid reciter.")
    
    if not TEMP_DIR.exists():
        TEMP_DIR.mkdir(parents=True)
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    surah_url = reciters[index]["mushaf"]["server"]
    successful_downloads = 0
    for surah_number in range(1, 115):
        surah_url = surah_url + f"/{surah_number:03d}.mp3"
        surah_response = requests.get(surah_url)

        if surah_response.status_code == 200:
            surah_file_path = TEMP_DIR / f"{surah_number:03d}.mp3"
            with open(surah_file_path, "wb") as f:
                    f.write(surah_response.content)
            print(f"Downloaded Surah {surah_number:03d}")
            successful_downloads += 1
        else:
            print(f"Failed to download Surah {surah_number:03d}")
            with open(TEMP_DIR / "failed_downloads.txt", "a") as f:
                f.write(f"Surah {surah_number:03d} failed to download.\n")
    
    print(f"Successfully downloaded {successful_downloads} surahs.")

    def merge_audio_files():
        audio_clips = []
        for surah_number in range(1, 115):
            surah_file_path = TEMP_DIR / f"{surah_number:03d}.mp3"
            if surah_file_path.exists():
                audio_clips.append(AudioFileClip(str(surah_file_path)))

        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(str(OUTPUT_DIR / "quran.mp3"))
            print("Merged all surahs into a single audio file.")

        for surah_number in range(1, 115):
            surah_file_path = TEMP_DIR / f"{surah_number:03d}.mp3"
            if surah_file_path.exists():
                surah_file_path.unlink()

#==================================================================================================
if __name__ == "__main__":
    DownloadWholeQuran()
    merge_audio_files()