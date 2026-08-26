# -*- coding: utf-8 -*-
from flask import Flask, render_template, Response, send_from_directory, jsonify
import cv2
import os
import datetime
import glob
import time
import json
from deepface import DeepFace

app = Flask(__name__)
camera = cv2.VideoCapture(0)
ultimul_cadru = None
detectie_text = "Se scaneaza..."

FOLDER_CAPTURI = "capturi"

if not os.path.exists(FOLDER_CAPTURI):
    os.makedirs(FOLDER_CAPTURI)

def generate_frames():
    global ultimul_cadru, detectie_text
    numar_cadru = 0
    
    culori_emotii = {
        'Fericit': (0, 255, 0),        
        'Trist': (255, 0, 0),          
        'Furios': (0, 0, 255),         
        'Surprins': (255, 255, 0),     
        'Dezgustat': (0, 128, 128),    
        'Speriat': (0, 165, 255),      
        'Dispret': (128, 0, 128),      
        'Neutru': (255, 255, 255),     
        'Se scaneaza...': (180, 105, 255), 
        'Fata nedetectata': (0, 0, 255) 
    }

    time.sleep(1) 

    while True:
        success, frame = camera.read()
        if not success:
            camera.open(0) 
            continue
        
        numar_cadru += 1

        if numar_cadru % 45 == 0:
            try:
                rezultate = DeepFace.analyze(
                    frame, 
                    actions=['emotion', 'age', 'gender'], 
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                
                if rezultate and len(rezultate) > 0:
                    res = rezultate[0]
                    regiune = res.get('region', {})
                    
                    if regiune.get('w', 0) > 10 and regiune.get('h', 0) > 10:
                        emotie = res['dominant_emotion']
                        dict_emotii = {
                            'happy': 'Fericit', 'sad': 'Trist', 'angry': 'Furios',
                            'surprise': 'Surprins', 'disgust': 'Dezgustat',
                            'fear': 'Speriat', 'contempt': 'Dispret', 'neutral': 'Neutru'
                        }
                        stare_ro = dict_emotii.get(emotie, emotie)
                        varsta = int(res['age'])
                        gen = res['dominant_gender']
                        gen_ro = "Femeie" if gen == "Woman" else "Barbat"
                        
                        detectie_text = f"Stare: {stare_ro} | Gen: {gen_ro} | Varsta: {varsta} ani"
                    else:
                        detectie_text = "Fata nedetectata"
                else:
                    detectie_text = "Fata nedetectata"
                    
            except Exception as e:
                detectie_text = "Fata nedetectata"

        # Variabila se numeste 'culoare' peste tot, fara alte denumiri in engleza
        culoare = (180, 105, 255) 
        for cheie in culori_emotii:
            if cheie in detectie_text:
                culoare = culori_emotii[cheie]
                break

        cv2.putText(frame, detectie_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, culoare, 2)
        h, w, _ = frame.shape
        cv2.rectangle(frame, (10, 10), (w-10, h-10), culoare, 2)

        ultimul_cadru = frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def analizeaza_dataset():
    # Calea catre folderul cu dataset-ul de test
    cale_dataset = os.path.join(os.getcwd(), 'dataset_test')
    
    # Daca folderul nu exista, il cream gol ca sa nu dea eroare programul
    if not os.path.exists(cale_dataset):
        os.makedirs(cale_dataset)
        return []

    statistici = []

    # Parcurgem fiecare folder din dataset_test (ex: "001", "002")
    for folder_varsta in sorted(os.listdir(cale_dataset)):
        cale_folder = os.path.join(cale_dataset, folder_varsta)
        
        if os.path.isdir(cale_folder):
            # Extragem varsta direct din numele folderului
            try:
                varsta_reala = int(folder_varsta)
            except ValueError:
                continue # Sari peste folder daca apar litere neasteptate

            numar_poze = 0
            suma_varste_estimate = 0
            suma_erori_absolute = 0

            # Luam TOATE pozele din folder, fara nicio limita
            toate_pozele = [p for p in os.listdir(cale_folder) if p.lower().endswith(('.png', '.jpg', '.jpeg'))]

            # Schimbare aici: iteram direct prin toate_pozele, nu doar prin primele 5
            for poza in toate_pozele:
                cale_poza = os.path.join(cale_folder, poza)
                numar_poze += 1
                
                try:
                    rezultat = DeepFace.analyze(img_path=cale_poza, actions=['age'], enforce_detection=False)
                    
                    if isinstance(rezultat, list):
                        varsta_estimata = rezultat[0]['age']
                    else:
                        varsta_estimata = rezultat['age']
                    
                    suma_varste_estimate += varsta_estimata
                    suma_erori_absolute += abs(varsta_estimata - varsta_reala)
                except Exception as e:
                    print(f"Eroare la procesarea pozei {poza}: {e}")
                    numar_poze -= 1

            if numar_poze > 0:
                medie_estimata = round(suma_varste_estimate / numar_poze, 1)
                eroare_medie = round(suma_erori_absolute / numar_poze, 1)
                
                statistici.append({
                    'grup': f"{varsta_reala} ani",
                    'total_poze': numar_poze,
                    'medie_ai': medie_estimata,
                    'eroare': eroare_medie
                })
                
    return statistici

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/salveaza_foto')
def salveaza_foto():
    global ultimul_cadru
    if ultimul_cadru is not None and ultimul_cadru.size > 0:
        nume_fisier = datetime.datetime.now().strftime("captura_%Y%m%d_%H%M%S.jpg")
        cale_salvare = os.path.join(FOLDER_CAPTURI, nume_fisier)
        cv2.imwrite(cale_salvare, ultimul_cadru)
        return f"S-a salvat: {nume_fisier}"
    return "Eroare: Camera inca se incarca sau nu trimite date...", 500

@app.route('/lista_poze')
def lista_poze():
    cale_cautare = os.path.join(FOLDER_CAPTURI, "captura_*.jpg")
    imagini = glob.glob(cale_cautare)
    imagini_curatate = [os.path.basename(img) for img in imagini]
    imagini_curatate.sort(reverse=True)
    return {"imagini": imagini_curatate}

@app.route('/imagini/<filename>')
def custom_static(filename):
    cale_folder_complet = os.path.join(os.getcwd(), FOLDER_CAPTURI)
    return send_from_directory(cale_folder_complet, filename)

@app.route('/galerie')
def pagina_mea_galerie():
    return render_template('galerie.html')

@app.route('/statistici')
def pagina_statistici():
    # Aceasta ruta doar va deschide noua pagina web pe care o vom crea
    return render_template('statistici.html')

@app.route('/ruleaza_test_dataset')
def ruleaza_test_dataset():
    # 1. Ruleaza analiza pe tot setul mare
    date_statistice = analizeaza_dataset()
    
    # 2. Salveaza o copie a rezultatelor intr-un fisier pe laptop
    with open('rezultate_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(date_statistice, f, indent=4, ensure_ascii=False)
        
    print("Toate pozele au fost analizate! Rezultatele au fost salvate in 'rezultate_dataset.json'")
    
    return jsonify({'statistici': date_statistice})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
