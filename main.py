
import requests
import subprocess
from pathlib import Path

# ============================================================
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

RECITERS_API_URL = "https://www.mp3quran.net/api/v3/reciters?language=eng"

# ============================================================

def DownloadWholeQuran():
    response = requests.get(RECITERS_API_URL, timeout=30)
    response.raise_for_status()

    reciters = response.json()["reciters"]

    print("Available Reciters:")
    for index, reciter in enumerate(reciters, start=1):
        print(f" - {index}. {reciter['name']}")

    while True:
        try:
            index = int(input("Select a reciter by number: ")) - 1

            if 0 <= index < len(reciters):
                break

            print("Invalid selection.")

        except ValueError:
            print("Please enter a number.")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    base_url = reciters[index]["moshaf"][0]["server"].rstrip("/")

    successful_downloads = 0

    for surah_number in range(1, 115):
        surah_url = f"{base_url}/{surah_number}.mp3"
        surah_file_path = TEMP_DIR / f"{surah_number:03d}.mp3"

        try:
            surah_response = requests.get(surah_url,timeout=60)
            surah_response.raise_for_status()
            surah_file_path.write_bytes(surah_response.content)
            print(f"Downloaded Surah {surah_number:03d}")
            successful_downloads += 1

        except requests.RequestException as error:
            print(f"Failed Surah {surah_number:03d}: {error}")

    print(f"Successfully downloaded {successful_downloads}/114 surahs.")


# ============================================================

def MergeAudioFiles():
    files = []
    for surah_number in range(1, 115):
        path = TEMP_DIR / f"{surah_number:03d}.mp3"

        if not path.exists():
            print(f"Missing Surah {surah_number:03d}")
            return

        if path.stat().st_size == 0:
            print(f"Empty file: {path.name}")
            return

        files.append(path)

    # Generate FFmpeg concat list
    list_path = TEMP_DIR / "files.txt"

    with open(list_path, "w", encoding="utf-8") as file:
        for path in files:
            file.write(f"file '{path.name}'\n")

    output_path = OUTPUT_DIR / "quran.mp3"

    command = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_path),
        "-map", "0:a:0",
        "-c:a", "copy",
        str(output_path)
    ]

    try:
        subprocess.run(
            command,
            cwd=TEMP_DIR,
            check=True
        )

        print("Successfully merged all surahs!")

    except subprocess.CalledProcessError:
        print("FFmpeg merging failed.")

    finally:
        list_path.unlink(missing_ok=True)

    # IMPORTANT:
    # Original MP3 files are intentionally preserved.


# ============================================================

if __name__ == "__main__":
    DownloadWholeQuran()
    MergeAudioFiles()
