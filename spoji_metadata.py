import os

# Putanja do foldera gde se nalaze tvoji metadata0.csv, metadata1.csv...
radni_folder = r"C:\TTS_Projekt\srpski_dataset"
izlazni_fajl = os.path.join(radni_folder, "metadata.csv")

# Broj govornika koje imaš (0, 1, 2 i 3 znači ukupno 4)
broj_govornika = 4 

with open(izlazni_fajl, 'w', encoding='utf-8') as izlaz:
    for i in range(broj_govornika):
        govornik = f"speaker{i}"
        # Očekivani nazivi fajlova su metadata0.csv, metadata1.csv, itd.
        ulazni_fajl = os.path.join(radni_folder, f"metadata{i}.csv")
        
        if not os.path.exists(ulazni_fajl):
            print(f"Upozorenje: Nije pronađen fajl {ulazni_fajl}. Preskačem...")
            continue
            
        with open(ulazni_fajl, 'r', encoding='utf-8') as ulaz:
            for linija in ulaz:
                linija = linija.strip()
                if not linija:
                    continue
                
                delovi = linija.split('|')
                if len(delovi) >= 2:
                    id_fajla = delovi[0]  # Uzima npr. 'a1'
                    tekst = delovi[1]     # Uzima prvu kolonu sa tekstom
                    
                    # Kreiranje novog reda u formatu: speaker0/a1|speaker0|tekst
                    novi_red = f"{govornik}/{id_fajla}|{govornik}|{tekst}\n"
                    izlaz.write(novi_red)

print(f"Spajanje je uspešno završeno! Glavni fajl je kreiran: {izlazni_fajl}")