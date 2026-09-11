import os
import subprocess

# PROVERA PUTANJE: Kopiraj punu putanju do foldera gde su ti ffmpeg.exe i ffprobe.exe
FFMPEG_EXE = r"D:\PROJEKAT TTS SERBIAN\moje resenje\ffmpeg.exe"

izvorni_mp3_folder = r"D:\PROJEKAT TTS SERBIAN\audio fajlovi"
ciljni_wav_folder = r"D:\PROJEKAT TTS SERBIAN\piper_dataset\wavs"
os.makedirs(ciljni_wav_folder, exist_ok=True)

for filename in os.listdir(izvorni_mp3_folder):
    if filename.endswith(".mp3"):
        izlazni_fajl = os.path.join(ciljni_wav_folder, filename.replace(".mp3", ".wav"))
        ulazni_fajl = os.path.join(izvorni_mp3_folder, filename)
        
        print(f"Konvertujem: {filename}...")
        
        # OVO JE KLJUČ: apad=pad_dur=0.5 dodaje tišinu NA KRAJ pre nego što ffmpeg išta iseče
        # -ar 22050 -ac 1 su standardi za Piper
        komanda = [
            FFMPEG_EXE,
            "-i", ulazni_fajl,
            "-af", "apad=pad_dur=0.5",
            "-ar", "22050",
            "-ac", "1",
            "-sample_fmt", "s16",
            "-y",
            izlazni_fajl
        ]
        
        try:
            subprocess.run(komanda, check=True, capture_output=True)
            print(f"Uspešno: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Greška kod {filename}: {e.stderr.decode()}")

print("Završeno!")