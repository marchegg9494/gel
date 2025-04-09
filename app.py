
from flask import Flask, render_template, request
import csv, os

app = Flask(__name__)

CSV_PATH = "buoni_gelato.csv"

def carica_buoni():
    with open(CSV_PATH, newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)

def aggiorna_buono(codice):
    righe = []
    trovato = False
    with open(CSV_PATH, newline='') as file:
        reader = csv.DictReader(file)
        righe = list(reader)
    for riga in righe:
        if riga["Codice"] == codice:
            if riga["Usato"] == "No":
                riga["Usato"] = "Sì"
                trovato = True
    if trovato:
        with open(CSV_PATH, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Codice", "Usato"])
            writer.writeheader()
            writer.writerows(righe)
    return trovato

@app.route("/", methods=["GET", "POST"])
def index():
    messaggio = ""
    if request.method == "POST":
        codice = request.form["codice"].strip().upper()
        buoni = carica_buoni()
        trovato = next((b for b in buoni if b["Codice"] == codice), None)
        if not trovato:
            messaggio = f"❌ Codice {codice} non trovato"
        elif trovato["Usato"] == "Sì":
            messaggio = f"⚠️ Codice {codice} è già stato usato"
        else:
            aggiorna_buono(codice)
            messaggio = f"✅ Codice {codice} valido e marcato come usato"
    return render_template("index.html", messaggio=messaggio)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
