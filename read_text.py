import os
import re
import subprocess
import numpy as np
import soundfile as sf
from datetime import datetime
import time  # <-- NOVO: Dodajemo modul za merenje vremena (štopericu)

_ZAMENE_OSNOVNE = [('.', ', tačka, '), ('-', ', crtica, '), ('_', ', donja crta, ')]
_ZAMENE_URL = [('.', ', tačka, '), ('/', ', kosa crta, '), ('-', ', crtica, '),
               ('_', ', donja crta, '), ('?', ', upitnik, '), ('=', ', jednako, ')]


def _sredi_rs_com(s: str) -> str:
    s = re.sub(r'\brs\b', 'R S', s, flags=re.IGNORECASE)
    return re.sub(r'\bcom\b', 'kom', s, flags=re.IGNORECASE)


def obradi_linkove_i_emailove(text: str) -> str:
    """ Sporije čitanje linkova (sa više zareza) i čitanje email-a kao 'imejl' """

    def zameni_email(match):
        email = match.group(0)
        email = email.replace('@', ', et, ')  # Znak @ sada čita kao "et"
        email = email.replace('.', ', tačka, ')
        email = email.replace('-', ', crtica, ')
        email = email.replace('_', ', donja crta, ')
        return f" {_sredi_rs_com(email)} "

    def zameni_url(m):
        u = m.group(0)
        u = u.replace('https://', 'ha te te pe es, dvotačka dve kose crte, ')
        u = u.replace('http://', 'ha te te pe, dvotačka dve kose crte, ')
        # OVO JE FALILO: Moramo i ovde tačku pretvoriti u reč!
        u = u.replace('.', ' tačka ') 
        
        for a, b in _ZAMENE_URL:
            u = u.replace(a, b)
        return f" {_sredi_rs_com(u)} "

    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', zameni_email, text)
    text = re.sub(r'https?://[^\s]+', zameni_url, text)
    text = re.sub(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', zameni_url, text)
    return text


def pametno_iseci_tekst(text: str):
    tm = obradi_linkove_i_emailove(text)
    tm = re.sub(r'\n([a-z])\.', r'\n\1_NABRAJANJE', tm)
    tm = re.sub(r'\b(br)\.', r'\1_SKRACENICA', tm, flags=re.IGNORECASE)

    pattern = r'(?<=[a-zšđžčć\)])\.\s+(?=[A-ZŠĐŽČĆa-z0-9])|(?<=[a-zšđžčć\)])\.\n'
    segmenti = []
    for seg in re.split(pattern, tm):
        seg = re.sub(r'([a-z])_NABRAJANJE', r'\1.', seg)
        seg = re.sub(r'\bbr_SKRACENICA\b', 'br.', seg, flags=re.IGNORECASE).strip()
        if seg:
            if not seg.endswith(('.', '!', '?')):
                seg += '.'
            segmenti.append(seg)

    return _spoji_kratke_segmente(segmenti)


def _spoji_kratke_segmente(segmenti, min_reci: int = 20):
    if len(segmenti) <= 1:
        return segmenti

    spojeno = []
    i = 0
    while i < len(segmenti):
        seg = segmenti[i]
        if len(seg.split()) < min_reci and spojeno:
            spojeno[-1] = spojeno[-1] + " " + seg
        elif len(seg.split()) < min_reci and i + 1 < len(segmenti):
            segmenti[i + 1] = seg + " " + segmenti[i + 1]
        else:
            spojeno.append(seg)
        i += 1
    return spojeno


def ocisti_segment_za_citanje(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\r', '')).replace('@', ' et ')
    # --- NOVO: Preslovljavanje cele ćirilice u latinicu NA SAMOM POČETKU ---
    cir_lat = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Đ', 'Е': 'E', 'Ж': 'Ž', 'З': 'Z', 'И': 'I',
        'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'Č', 'Џ': 'Dž', 'Ш': 'Š',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'đ', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'i',
        'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š'
    }
    for cir, lat in cir_lat.items():
        text = text.replace(cir, lat)
    # Reč "email" čitamo kao "imejl"
    text = re.sub(r'\be-?mail\b', 'imejl', text, flags=re.IGNORECASE)

    # --- NOVO: Čitanje stranih reči i brendova (fonetski) ---
    text = re.sub(r'\bmastercard\b', 'masterkard', text, flags=re.IGNORECASE)
    text = re.sub(r'\bvisa\b', 'viza', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSHA\b', 'ša', text, flags=re.IGNORECASE)
    text = re.sub(r'\bBEN\b', 'ben', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\bOUP\b', 'oup', text, flags=re.IGNORECASE)
    # Čitanje kose crte kao pauze (npr. otvaranje/zamenu -> otvaranje, zamenu)
    text = re.sub(r'(?<=[a-zA-ZšđžčćŠĐŽČĆ])/(?=[a-zA-ZšđžčćŠĐŽČĆ])', ', ', text)

    # Čitanje zagrada
    text = re.sub(r'\((.*?)\)', r'zagrada, \1, zatvorena zagrada', text)

    # Hvatamo datum ZAJEDNO sa poslednjom tačkom (kao jednu celinu)
    dates = []
    text = re.sub(r'\b\d{1,2}\.\d{1,2}\.\d{4}\.', 
                  lambda m: dates.append(m.group(0)) or f"__DATE_{len(dates) - 1}__", text)

    # Postojeće pravilo za novac
    money = []
    text = re.sub(r'\b\d+(?:\.\d{3})*,\d{2}\b',
                   lambda m: money.append(m.group(0)) or f"__MONEY_{len(money) - 1}__", text)
    # --- NOVO: Pravilo za cele brojeve sa tačkom (npr. 8.000, 10.000, 1.500.000) ---
    veliki_brojevi = []
    text = re.sub(r'\b\d{1,3}(?:\.\d{3})+\b',
                  lambda m: veliki_brojevi.append(m.group(0)) or f"__THOUSANDS_{len(veliki_brojevi) - 1}__", text)

    text = re.sub(r'(?<![\d-])\b(\d{1,4})-(\d{1,4})\b(?![\d-])', r'\1 do \2', text)
    text = re.sub(r'\+\d[\d\s-]*\d', lambda m: "plus " + " ".join(c for c in m.group(0) if c.isdigit()), text)
    text = re.sub(r'\b\d+(?:-\d+)+\b', lambda m: " ".join(c for c in m.group(0) if c.isdigit()), text)
    text = re.sub(r'\b\d{6,}\b', lambda m: " ".join(c for c in m.group(0) if c.isdigit()), text)

    text = re.sub(r'\b(\d+)\.(\d+)\.', r'\1 tačka \2,', text)
    text = re.sub(r'\b(\d+)\.(\d+)\b', r'\1 tačka \2', text)
    text = re.sub(r'\b(\d+)\.', r'\1,', text)

    skracenice = {
        #r"\bPIO\b": "pio",
        r"\brs\b": "r s",
        #r"\buspostavljanje\b": "uspostavljan je",
        #r"\bposlovanja\b": "poslova nja",
        #r"\bosiguranja\b": "osigu ranja",
        #r"\bperiodična\b": "periodič na",
        r"\bwww\b": "duplo ve duplo ve duplo ve",
        r"\bEKS\b": "efektivne kamatne stope",
        #r"\bPIB\b": "pib", 
        #r"\bračuna\b": "ra čuna", 
        #r"\bračun\b": "ra čun", 
        #r"\bpaketa\b": "paketa", 
        #r"\buređuju\b": "ure đuju", 
        r"\bhumanitarne\b": "humanitar ne",
        #r"\bpaketu\b": "pa ketu",
        #r"\bkamatna\b": "kama tna",
        #r"\bkamatne\b": "kama tne",
        #r"\bJMBG\b": "je em be ge", 
        #r"\bjednokratno\b": "jednokrat no",
        #r"\bminimalno\b": "minimal no",
        #r"\bmaksimalno\b": "maksimal no",
        #r"\bNBS\b": "en be es",
        r"\bSMS\b": "es em es",
        r"\bQR\b": "kju ar",
        r"\bKB\b": "kreditni biro",
        r"\bLK\b": "lična karta",
        r"\bNBS\b": "narodne banke srbije"
    }
    for sablon, zamena in skracenice.items():
        text = re.sub(sablon, zamena, text, flags=re.IGNORECASE)
    text = re.sub(r'\bbr\.', 'broj', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbr\b(?=\s*\d)', 'broj', text, flags=re.IGNORECASE)
    #Menjamo "min." i "maks." u pune reči i brišemo tačku
    text = re.sub(r'\bmin\.', 'minimalno', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmaks\.', 'maksimalno', text, flags=re.IGNORECASE)
    #text = re.sub(r'\bmin\b(?=\s*\d)', 'minimalno', text, flags=re.IGNORECASE)
    #text = re.sub(r'\bmaks\b(?=\s*\d)', 'maksimalno', text, flags=re.IGNORECASE)
    #text = re.sub(r'\bbr\.?\b', 'broj', text, flags=re.IGNORECASE)
    # Skraćeno min. i maks. pretvaramo DIREKTNO u pune reči
    #text = re.sub(r'\bmin\.', 'minimalno ', text, flags=re.IGNORECASE)
    #text = re.sub(r'\bmaks\.', 'maksimalno ', text, flags=re.IGNORECASE)
    
    # --- POBOLJŠANO: Skraćeno min. i maks. (bez strogih granica reči) ---
    #text = re.sub(r'(?<![a-zA-Z])min\.', 'minimalno ', text, flags=re.IGNORECASE)
    #text = re.sub(r'(?<![a-zA-Z])maks\.', 'maksimalno ', text, flags=re.IGNORECASE)
   # --- POBOLJŠANO: Čitanje valuta (radi čak i ako je spojeno sa brojem, npr. 150RSD) ---
    valute = {
        'RSD': 'dinara',
        'РСД': 'dinara',
        'EUR': 'evra',
        'USD': 'američkih dolara',
        'CHF': 'švajcarskih franaka',
        'GBP': 'britanskih funti'
    }
    for oznaka, naziv in valute.items():
        # (?<![a-zA-Z]) i (?![a-zA-Z]) znače: "Samo ako pre i posle valute nisu druga slova"
        text = re.sub(rf'(?<![a-zA-Z]){oznaka}(?![a-zA-Z])', naziv, text, flags=re.IGNORECASE)

    # Vraćamo novac
    for idx, orig in enumerate(money):
        text = text.replace(f"__MONEY_{idx}__", orig.replace('.', ' ').replace(',', ' zarez '))
    
    # --- NOVO: Vraćamo velike brojeve bez tačke (8.000 -> 8000) ---
    for idx, orig in enumerate(veliki_brojevi):
        text = text.replace(f"__THOUSANDS_{idx}__", orig.replace('.', ''))

    # --- NOVO: Rečnici za pretvaranje brojeva u reči ---
    meseci_imena = {
        1: "januara", 2: "februara", 3: "marta", 4: "aprila",
        5: "maja", 6: "juna", 7: "jula", 8: "avgusta",
        9: "septembra", 10: "oktobra", 11: "novembra", 12: "decembra"
    }
    
    dani_imena = [
        "", "prvog", "drugog", "trećeg", "četvrtog", "petog", "šestog", "sedmog", "osmog", "devetog", "desetog",
        "jedanaestog", "dvanaestog", "trinaestog", "četrnaestog", "petnaestog", "šesnaestog", "sedamnaestog", "osamnaestog", "devetnaestog", "dvadesetog",
        "dvadeset prvog", "dvadeset drugog", "dvadeset trećeg", "dvadeset četvrtog", "dvadeset petog", "dvadeset šestog", "dvadeset sedmog", "dvadeset osmog", "dvadeset devetog", "tridesetog", "trideset prvog"
    ]

    # Vraćamo datume i prevodimo ih direktno u reči
    # Vraćamo datume i prevodimo ih direktno u reči
    for idx, orig in enumerate(dates):
        try:
            # Sklanjamo poslednju tačku da bi strptime lakše parsirao
            cist_datum = orig.rstrip('.')
            
            datum = datetime.strptime(cist_datum, "%d.%m.%Y")
            dan = datum.day       
            mesec = datum.month   
            godina = datum.year   
            
            ime_dana = dani_imena[dan]
            ime_meseca = meseci_imena.get(mesec, str(mesec))
            
            # --- MAGIJA ZA GODINU ---
            zadnja_dva = godina % 100
            zadnja_cifra = godina % 10
            
            if 10 <= zadnja_dva <= 19:
                sufiksi_teen = {10: "desete", 11: "jedanaeste", 12: "dvanaeste", 13: "trinaeste", 14: "četrnaeste", 15: "petnaeste", 16: "šesnaeste", 17: "sedamnaeste", 18: "osamnaeste", 19: "devetnaeste"}
                godina_tekst = f"{godina - zadnja_dva} {sufiksi_teen[zadnja_dva]}" # npr. 2015 -> 2000 petnaeste
            elif zadnja_cifra == 0:
                godina_tekst = f"{godina}." # Okrugle godine (npr. 2020.) čita kako treba
            else:
                sufiksi = {1: "prve", 2: "druge", 3: "treće", 4: "četvrte", 5: "pete", 6: "šeste", 7: "sedme", 8: "osme", 9: "devete"}
                godina_tekst = f"{godina - zadnja_cifra} {sufiksi[zadnja_cifra]}" # npr. 2025 -> 2020 pete
                
            # Formatiramo datum tako da Piper dobije 100% tekstualne komande
            uredjen_datum = f"{ime_dana} {ime_meseca} {godina_tekst} godine. "
            
        except ValueError:
            # Ako nije pravi datum, vraćamo ga kakav je i bio
            uredjen_datum = orig
            
        text = text.replace(f"__DATE_{idx}__", uredjen_datum)
            
        

    text = text.strip()
    if text.endswith(','):
        text = text[:-1] + '.'
    elif not text.endswith('.'):
        text += '.'
    return text


def generisi_audio(txt_path, piper_exe, model_path, config_path, espeak_data_path, output_wav):
    if not os.path.exists(txt_path):
        print(f"Greška: Fajl '{txt_path}' nije pronađen.")
        return

    with open(txt_path, 'r', encoding='utf-8') as f:
        original_text = f.read()

    segmenti = pametno_iseci_tekst(original_text)
    audio_parts = []
    sr = 22050

    # Varijable za izračunavanje RTF-a na nivou celog procesa
    ukupno_vreme_generisanja = 0.0
    ukupno_trajanje_zvuka = 0.0

    print("Počinjem generisanje. Molim te sačekaj...")

    for i, seg in enumerate(segmenti):
        clean_seg = ocisti_segment_za_citanje(seg)
        if not clean_seg:
            continue

        speaker_id = "0"
        temp_wav = f"temp_{i}.wav"
        cmd = [
            piper_exe, "--model", model_path, "--config", config_path,
            "--espeak_data", espeak_data_path, "--language", "sr",
            "--length-scale", "1.4", "--noise_scale", "0.667", "--noise_w", "0.8",
            "--speaker", speaker_id,
            "--output_file", temp_wav
        ]
        
        # POKREĆEMO ŠTOPERICU pre nego što Piper počne
        start_time = time.time()
        
        subprocess.run(cmd, input=clean_seg, text=True, encoding="utf-8", capture_output=True)
        
        # ZAUSTAVLJAMO ŠTOPERICU kada je fajl završen
        end_time = time.time()
        vreme_obrade = end_time - start_time
        ukupno_vreme_generisanja += vreme_obrade

        if os.path.exists(temp_wav):
            y, _ = sf.read(temp_wav)
            audio_parts.append(y)
            
            # Računamo koliko sekundi traje sam zvuk
            trajanje_segmenta = len(y) / sr
            ukupno_trajanje_zvuka += trajanje_segmenta
            
            os.remove(temp_wav)
            if i < len(segmenti) - 1:
                audio_parts.append(np.zeros(int(sr * 1)))  #  pauza između segmenata

    if audio_parts:
        sf.write(output_wav, np.concatenate(audio_parts), sr)
        print(f"\nUspešno završen posao! Finalni fajl: {output_wav}")
        
        # ISPIS RTF STATISTIKE
        if ukupno_trajanje_zvuka > 0:
            rtf = ukupno_vreme_generisanja / ukupno_trajanje_zvuka
            print("-" * 40)
            print("📊 STATISTIKA GENERISANJA (Real Time Factor):")
            print(f"⏱️  Kompjuteru je trebalo: {ukupno_vreme_generisanja:.2f} sekundi")
            print(f"🔊 Generisani zvuk traje: {ukupno_trajanje_zvuka:.2f} sekundi")
            print(f"⚡ RTF iznosi: {rtf:.4f}")
            print("-" * 40)
    else:
        print("\nGreška pri generisanju.")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    generisi_audio(
        txt_path=os.path.join(BASE_DIR, "tekst1.txt"),
        piper_exe=os.path.join(BASE_DIR, "piper.exe"),
        model_path=os.path.join(BASE_DIR, "model.onnx"),
        config_path=os.path.join(BASE_DIR, "model.onnx.json"),
        espeak_data_path=os.path.join(BASE_DIR, "espeak-ng-data"),
        output_wav=os.path.join(BASE_DIR, "multiple_speaker_0_v14.wav")
    )