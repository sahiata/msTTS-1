import os
import glob
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Putanje
input_folder = r"C:\TTS_Projekt\Novi_zvuk_4"
output_folder = os.path.join(input_folder, "isecene_recenice")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Pronalazi sve .wav fajlove u glavnom folderu
wav_files = glob.glob(os.path.join(input_folder, "*.wav"))

if not wav_files:
    print(f"Nije pronađen nijedan .wav fajl u folderu: {input_folder}")
    exit()

print(f"Pronađeno ukupno {len(wav_files)} .wav fajlova za obradu.\n")

# Globalni brojač za imenovanje fajlova (a1, a2, a3...)
global_counter = 1

# Prolazimo kroz svaki fajl
for file_index, file_path in enumerate(wav_files, start=1):
    file_name = os.path.basename(file_path)
    print(f"[{file_index}/{len(wav_files)}] Obrađujem: {file_name}")
    
    try:
        # Učitavanje audia
        audio = AudioSegment.from_file(file_path)
        
        # PODEŠAVANJA ZA STROŽIJE SEČENJE:
        # Smanjujemo min_silence_len na 800ms da bismo uhvatili kraće pauze između rečenica
        # Podižemo silence_thresh na -45dB da skripta lakše prepozna tišinu uprkos šumu
        chunks = split_on_silence(
            audio,
            min_silence_len=800,    # Tišina sada mora trajati bar 800ms
            silence_thresh=-45,     # Prag tišine podignut na -45 dBFS (agresivnije sečenje)
            keep_silence=400        # Ostavlja 250ms tišine na početku i kraju za prirodan TTS prelaz
        )
        
        # Čuvanje isečenih delova direktno u zajednički folder sa linearnom numeracijom
        for chunk in chunks:
            output_path = os.path.join(output_folder, f"a{global_counter}.wav")
            
            # PROMENJENO: Eksportujemo na 22050Hz, mono (1 kanal)
            chunk = chunk.set_frame_rate(22050).set_channels(1)
            chunk.export(output_path, format="wav")
            
            global_counter += 1
            
        print(f" -> Uspešno isečeno i dodato {len(chunks)} rečenica.\n")
        
    except Exception as e:
        print(f" -> Greška pri obradi fajla {file_name}: {e}\n")

print(f"Svi fajlovi su uspešno obrađeni!")
print(f"Ukupno je generisano {global_counter - 1} rečenica (od a1 do a{global_counter - 1}).")
print(f"Svi fajlovi se nalaze direktno u: {output_folder}")