from flask import Flask, render_template, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

CSV_PATH = "buoni_gelato.csv"

def carica_buoni():
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        app.logger.error(f"Errore nel caricamento dei buoni: {e}")
        return []

def aggiorna_buono(codice):
    """Aggiorna lo stato del buono da 'No' a 'Sì' e aggiunge data di utilizzo"""
    try:
        righe = []
        trovato = False
        with open(CSV_PATH, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            if "DataUtilizzo" not in headers:
                headers = headers + ["DataUtilizzo"]
            righe = list(reader)
        
        for riga in righe:
            if riga["Codice"] == codice:
                if riga["Usato"] == "No":
                    riga["Usato"] = "Sì"
                    # Aggiunge la data di utilizzo (formato italiano)
                    riga["DataUtilizzo"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    trovato = True
        
        if trovato:
            with open(CSV_PATH, "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(righe)
        return trovato
    except Exception as e:
        app.logger.error(f"Errore nell'aggiornamento del buono: {e}")
        return False

def get_stats():
    """Restituisce statistiche sui buoni"""
    buoni = carica_buoni()
    totale = len(buoni)
    usati = sum(1 for b in buoni if b.get("Usato") == "Sì")
    disponibili = totale - usati
    return {
        "totale": totale,
        "usati": usati,
        "disponibili": disponibili,
        "percentuale_usati": round((usati / totale) * 100) if totale > 0 else 0
    }

@app.route("/", methods=["GET", "POST"])
def index():
    messaggio = ""
    tipo_messaggio = ""
    stats = get_stats()
    
    if request.method == "POST":
        codice = request.form["codice"].strip().upper()
        buoni = carica_buoni()
        trovato = next((b for b in buoni if b["Codice"] == codice), None)
        
        if not trovato:
            messaggio = f"Codice {codice} non trovato"
            tipo_messaggio = "error"
        elif trovato["Usato"] == "Sì":
            data_uso = trovato.get("DataUtilizzo", "data sconosciuta")
            messaggio = f"Codice {codice} è già stato usato il {data_uso}"
            tipo_messaggio = "warning"
        else:
            aggiorna_buono(codice)
            messaggio = f"Codice {codice} valido e marcato come usato"
            tipo_messaggio = "success"
            # Aggiorna le statistiche dopo l'utilizzo
            stats = get_stats()
            
    return render_template("index.html", messaggio=messaggio, tipo_messaggio=tipo_messaggio, stats=stats)

@app.route("/stats", methods=["GET"])
def statistiche():
    """Endpoint API per ottenere statistiche in formato JSON"""
    return jsonify(get_stats())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug="FLASK_DEBUG" in os.environ)
