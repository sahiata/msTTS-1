import os
import csv
import re
import whisper
import torch
from num2words import num2words
os.environ["PATH"] += os.path.pathsep + r"C:\Program Files\FFmpeg\bin"

# 1. Provera hardvera
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Koristim uređaj: {device.upper()}")

# 2. Učitavanje Whisper modela
print("Učitavam Whisper Large-v3 model...")
model = whisper.load_model("large-v3", device=device)

# 3. FIKSNE PUTANJE (Eksplicitno zadate)
audio_folder = r"C:\TTS_Projekt\Novi_zvuk_3\wav"
output_csv = os.path.join(audio_folder, "metadata.csv")

print(f"Audio fajlovi se učitavaju iz: {audio_folder}")
print(f"Metadata fajl će biti sačuvan u: {output_csv}")

# Funkcija koja automatski pretvara sve brojeve iz teksta u srpske reči
def pretvori_brojeve_u_tekst(tekst):
    # Prvo čistimo tačke u brojevima (npr. 340.000 -> 340000) kako bi algoritam prepoznao ceo broj
    tekst_bez_tacaka = re.sub(r'(?<=\d)\.(?=\d)', '', tekst)
    
    # Pronalazimo sve brojeve u tekstu
    brojevi = re.findall(r'\d+', tekst_bez_tacaka)
    
    # Sortiramo ih od najvećih ka najmanjim da ne bi prepisao delove brojeva greškom
    for broj in sorted(brojevi, key=len, reverse=True):
        try:
            # Pretvaramo broj u reči na srpskom jeziku (sr)
            reci = num2words(int(broj), lang='sr')
            # Zamenjujemo cifre rečima u tekstu
            tekst_bez_tacaka = tekst_bez_tacaka.replace(broj, reci)
        except Exception:
            pass
            
    return tekst_bez_tacaka

# 4. Prompt za Whisper
srpski_prompt = (
    "Ovo je tačan transkript na srpskom jeziku sa svim slovima č, ć, š, ž, đ. "
    "Sve brojeve, cifre i godine obavezno piši isključivo slovima, nikako ciframa! "
    "Primeri: od prvog do šestog januara hiljadu devetsto četrdesete godine, "
    "anđeli, carstvo zemaljsko, slonovača, mermer, zaplakaće, pročitati, izađe, reči."
)

# 5. Pokretanje transkripcije
with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='|')
    
    sve_u_folderu = os.listdir(audio_folder)
    audio_files = sorted([file for file in sve_u_folderu if file.endswith(('.wav', '.mp3', '.m4a'))])
    
    for filename in audio_files:
        file_id = os.path.splitext(filename)[0]
        file_path = os.path.join(audio_folder, filename)
        
        print(f"Transkribujem i peglam brojeve: {filename}...")
        
        result = model.transcribe(
            file_path,
            language="sr",
            initial_prompt=srpski_prompt,
            temperature=0.0,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6
        )
        
        sirovi_tekst = result["text"].strip()
        
        # Pretvaramo sve cifre u reči na srpskom
        cist_tekst = pretvori_brojeve_u_tekst(sirovi_tekst)
        
        # Upisujemo u formatu za TTS: id_fajla|tekst|tekst
        writer.writerow([file_id, cist_tekst, cist_tekst])

print(f"\nGotovo! Podaci sa kvačicama i BEZ BROJEVA su sačuvani u: {output_csv}")