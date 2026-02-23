import random
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

# Configurazione
NUM_PERSONE = 60
PERSONE_PER_PERIODO = 10
PERSONE_PER_RIPOSO = 10
NUM_RIPOSI = 6
NUM_PERIODI = 6

# Periodi di ferie
PERIODI = {
    'periodo_1': {'inizio': (6, 10), 'fine': (6, 26)},      # 10-26 giugno
    'periodo_2': {'inizio': (6, 27), 'fine': (7, 13)},      # 27 giugno - 13 luglio
    'periodo_3': {'inizio': (7, 14), 'fine': (7, 30)},      # 14-30 luglio
    'periodo_4': {'inizio': (7, 31), 'fine': (8, 16)},      # 31 luglio - 16 agosto
    'periodo_5': {'inizio': (8, 17), 'fine': (9, 2)},       # 17 agosto - 2 settembre
    'periodo_6': {'inizio': (9, 3), 'fine': (9, 19)},       # 3-19 settembre
}

# Giorni di inizio per ogni tipo di riposo
RIPOSI_INIZIO = {
    'riposo_1': (6, 9),    # 9 giugno
    'riposo_2': (6, 10),   # 10 giugno
    'riposo_3': (6, 11),   # 11 giugno
    'riposo_4': (6, 12),   # 12 giugno
    'riposo_5': (6, 13),   # 13 giugno
    'riposo_6': (6, 14),   # 14 giugno
}


def genera_giorni_riposo(tipo_riposo, anno=2026):
    """
    Genera i giorni di riposo per un tipo di riposo (pattern +6 giorni)
    Da giugno a settembre 2026
    """
    giorni = []
    mese, giorno = RIPOSI_INIZIO[tipo_riposo]

    data_inizio = datetime(anno, mese, giorno)
    data_fine = datetime(anno, 9, 30)  # Fine settembre

    data_corrente = data_inizio
    while data_corrente <= data_fine:
        giorni.append(data_corrente.date())
        data_corrente += timedelta(days=6)

    return giorni


def genera_giorni_ferie(periodo, anno=2026):
    """
    Genera la lista di giorni per un periodo di ferie
    """
    giorni = []
    mese_inizio, giorno_inizio = PERIODI[periodo]['inizio']
    mese_fine, giorno_fine = PERIODI[periodo]['fine']

    data_inizio = datetime(anno, mese_inizio, giorno_inizio)
    data_fine = datetime(anno, mese_fine, giorno_fine)

    data_corrente = data_inizio
    while data_corrente <= data_fine:
        giorni.append(data_corrente.date())
        data_corrente += timedelta(days=1)

    return giorni


def crea_assegnazioni_riposi():
    """
    Assegna a ogni persona un tipo di riposo (10 persone per tipo)
    Ritorna: lista di tuple (persona_id, tipo_riposo)
    """
    assegnazioni = []
    persona_id = 0

    for riposo_type in range(1, NUM_RIPOSI + 1):
        riposo_key = f'riposo_{riposo_type}'
        for _ in range(PERSONE_PER_RIPOSO):
            assegnazioni.append((persona_id, riposo_key))
            persona_id += 1

    return assegnazioni


def simula_una_combinazione():
    """
    Simula UNA combinazione di periodi di ferie assegnati casualmente
    Ritorna: dizionario con la data e il numero di persone assenti
    """
    # Assegnazioni fisse dei riposi (10 persone per riposo type)
    assegnazioni_riposi = crea_assegnazioni_riposi()

    # Assegna casualmente i periodi di ferie (10 persone per periodo)
    periodi_list = list(PERIODI.keys())
    assegnazioni_periodi = []

    for periodo in periodi_list:
        for _ in range(PERSONE_PER_PERIODO):
            assegnazioni_periodi.append(periodo)

    random.shuffle(assegnazioni_periodi)

    # Crea una mappa persona -> (riposo, periodo)
    assegnazioni = {}
    for i, (persona_id, riposo) in enumerate(assegnazioni_riposi):
        assegnazioni[persona_id] = {
            'riposo': riposo,
            'periodo': assegnazioni_periodi[i]
        }

    # Conta le persone assenti per ogni giorno
    assenti_per_giorno = defaultdict(int)

    for persona_id, assegnazione in assegnazioni.items():
        riposo_type = assegnazione['riposo']
        periodo = assegnazione['periodo']

        # Giorni di riposo per questa persona
        giorni_riposo = genera_giorni_riposo(riposo_type)
        for giorno in giorni_riposo:
            assenti_per_giorno[giorno] += 1

        # Giorni di ferie per questa persona
        giorni_ferie = genera_giorni_ferie(periodo)
        for giorno in giorni_ferie:
            assenti_per_giorno[giorno] += 1

    return assenti_per_giorno


def analizza_risultati(assenti_per_giorno):
    """
    Analizza i risultati di una simulazione e trova i giorni critici
    """
    giorni_20_plus = {}  # giorni con 20+ assenti
    giorni_30_plus = {}  # giorni con 30+ assenti

    for giorno, num_assenti in assenti_per_giorno.items():
        if num_assenti >= 30:
            giorni_30_plus[giorno] = num_assenti
        elif num_assenti >= 20:
            giorni_20_plus[giorno] = num_assenti

    return giorni_20_plus, giorni_30_plus


def esegui_simulazione(num_simulazioni=100):
    """
    Esegue multiple simulazioni e raccoglie statistiche
    """
    print(f"\n{'='*60}")
    print(f"SIMULAZIONE FERIE - {num_simulazioni} iterazioni")
    print(f"{'='*60}\n")

    # Statistiche per ogni giorno
    statistiche_giorni = defaultdict(lambda: {'count_20plus': 0, 'count_30plus': 0, 'valori': []})

    for sim_num in range(num_simulazioni):
        print(f"Simulazione {sim_num + 1}/{num_simulazioni}...", end='\r')

        assenti_per_giorno = simula_una_combinazione()
        giorni_20_plus, giorni_30_plus = analizza_risultati(assenti_per_giorno)

        # Registra i giorni critici
        for giorno in giorni_20_plus:
            statistiche_giorni[giorno]['count_20plus'] += 1
            statistiche_giorni[giorno]['valori'].append(giorni_20_plus[giorno])

        for giorno in giorni_30_plus:
            statistiche_giorni[giorno]['count_30plus'] += 1
            statistiche_giorni[giorno]['valori'].append(giorni_30_plus[giorno])

    print(f"\nSimulazioni completate!                                    \n")
    return statistiche_giorni


def stampa_risultati(statistiche_giorni):
    """
    Stampa i risultati in formato leggibile
    """
    print(f"\n{'='*60}")
    print("RISULTATI ANALISI")
    print(f"{'='*60}\n")

    # Giorni ordinati
    giorni_ordinati = sorted(statistiche_giorni.keys())

    if not giorni_ordinati:
        print("Nessun giorno critico (20+ assenti) trovato.")
        return

    # Tabella
    data_per_tabella = []
    for giorno in giorni_ordinati:
        stats = statistiche_giorni[giorno]
        media = sum(stats['valori']) / len(stats['valori']) if stats['valori'] else 0
        massimo = max(stats['valori']) if stats['valori'] else 0
        minimo = min(stats['valori']) if stats['valori'] else 0

        data_per_tabella.append({
            'Data': giorno.strftime('%d/%m/%Y'),
            'Giorno Settimana': giorno.strftime('%A'),
            'Volte 20+': stats['count_20plus'],
            'Volte 30+': stats['count_30plus'],
            'Media Assenti': f"{media:.1f}",
            'Min': minimo,
            'Max': massimo
        })

    df = pd.DataFrame(data_per_tabella)
    print(df.to_string(index=False))

    # Riassunto
    print(f"\n{'='*60}")
    print("RIASSUNTO GIORNI CRITICI")
    print(f"{'='*60}\n")

    giorni_30plus = [g for g in giorni_ordinati if statistiche_giorni[g]['count_30plus'] > 0]
    giorni_20plus = [g for g in giorni_ordinati if statistiche_giorni[g]['count_20plus'] > 0]

    if giorni_30plus:
        print(f"CRITICO! GIORNI CON 30+ ASSENTI ({len(giorni_30plus)} giorni):")
        for giorno in giorni_30plus:
            stats = statistiche_giorni[giorno]
            freq = (stats['count_30plus'] / len(statistiche_giorni)) * 100
            print(f"   - {giorno.strftime('%d/%m/%Y (%A)')}: {stats['count_30plus']} volte ({freq:.1f}%)")

    if giorni_20plus:
        print(f"\nATTENZIONE! GIORNI CON 20+ ASSENTI ({len(giorni_20plus)} giorni):")
        for giorno in giorni_20plus[:10]:  # Mostra primi 10
            stats = statistiche_giorni[giorno]
            freq = (stats['count_20plus'] / len(statistiche_giorni)) * 100
            print(f"   - {giorno.strftime('%d/%m/%Y (%A)')}: {stats['count_20plus']} volte ({freq:.1f}%)")


def genera_json_rischio(statistiche_giorni, num_simulazioni):
    """
    Genera il JSON con i dati di rischio per ogni giorno
    """
    import json
    from pathlib import Path

    output_data = {}

    for giorno, stats in statistiche_giorni.items():
        giorno_str = giorno.strftime('%Y-%m-%d')

        # Calcola le percentuali
        percentuale_20plus = (stats['count_20plus'] / num_simulazioni) * 100
        percentuale_30plus = (stats['count_30plus'] / num_simulazioni) * 100

        # Media, min, max assenti
        if stats['valori']:
            media = sum(stats['valori']) / len(stats['valori'])
            massimo = max(stats['valori'])
            minimo = min(stats['valori'])
        else:
            media = massimo = minimo = 0

        output_data[giorno_str] = {
            'percentuale_20plus': round(percentuale_20plus, 2),
            'percentuale_30plus': round(percentuale_30plus, 2),
            'media_assenti': round(media, 2),
            'max_assenti': massimo,
            'min_assenti': minimo,
            'count_20plus': stats['count_20plus'],
            'count_30plus': stats['count_30plus']
        }

    # Salva il JSON
    file_path = Path(__file__).parent / 'analisi_rischi.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nFile JSON generato: {file_path}")
    print(f"Totale giorni: {len(output_data)}")

    return file_path


if __name__ == "__main__":
    # Test: genera i periodi e riposi
    print("Test generazione periodi:")
    for periodo in PERIODI:
        giorni = genera_giorni_ferie(periodo)
        print(f"{periodo}: {len(giorni)} giorni")

    print("\nTest generazione riposi:")
    for i in range(1, 7):
        giorni = genera_giorni_riposo(f'riposo_{i}')
        print(f"riposo_{i}: {len(giorni)} giorni (primi 5: {giorni[:5]})")

    # Esegui simulazioni con 500 iterazioni
    print(f"\n{'='*60}")
    statistiche = esegui_simulazione(num_simulazioni=500)

    # Stampa risultati
    stampa_risultati(statistiche)

    # Genera JSON
    genera_json_rischio(statistiche, num_simulazioni=500)
