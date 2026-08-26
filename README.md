# Smart Home Emotional Assistant 🧠🏠

Un prototip hardware-software de tip nod IoT independent (Edge Computing) dezvoltat pe **Raspberry Pi 4**, conceput pentru captarea, identificarea și clasificarea stărilor emoționale în timp real.

> **Lucrare de Licență** – Universitatea Transilvania din Brașov (Facultatea de Inginerie Electrică și Știința Calculatoarelor - IESC)

---

## 📌 Descriere & Arhitectură Sistem

Sistemul utilizează analiza video non-invazivă a feței pe baza celor 7 emoții universale (Modelul Paul Ekman) și a macro-expresiilor (MaE). Întreaga procesare a cadrelor video are loc **local** (la marginea rețelei – Edge Computing) pe procesorul ARM al plăcii Raspberry Pi 4, protejând confidențialitatea datelor (conform normelor GDPR).

### Componente Principale:
* **Hardware Unit:** Raspberry Pi 4 Model B (8 GB RAM), Cameră Web Logitech C600, Adaptor USB 3.0-RJ45 (TP-LINK UE300).
* **AI & Processing Engine:** Python, OpenCV (prelucrare video / ROI), MTCNN (detecție facială), DeepFace (clasificare emoție/vârstă/gen).
* **Web Server & UI:** Flask Framework (Backend), HTML5/CSS3 în **Dark Mode** (Frontend), afișare de statistici și grafice în format JSON.
* **Networking & Administration:** Acces remote headless securizat prin SSH, SFTP (WinSCP), RealVNC și VPN privat prin Tailscale.

---

## 🚀 Optimizare & Performanțe Tehnică

Pentru a asigura o funcționare fluentă pe resurse hardware limitate, procesarea AI cu biblioteca DeepFace este eșantionată asincron (o dată la 45 de cadre).

* **Latență procesare:** 1.2s – 1.8s pe CPU-ul Raspberry Pi 4.
* **Rată de streaming live:** 24 – 26 FPS în rețeaua locală.
* **Management defensiv al erorilor:** Tratare automată a cazurilor de deconectare ale senzorului optic.

---

## 🗂️ Structura Proiectului

```text
proiect_web/
├── capturi/           # Capturi de imagini generate în format .jpg
├── static/            # Fișiere statice (style.css)
├── template/          # Șabloane HTML (index.html, galerie.html, statistici.html)
├── dataset_test/      # Imagini folosite pentru testare pe grupe de vârstă
├── rezultate_dataset.json  # Rezultatele salvate în format structurat
└── web_app.py         # Scriptul principal Python / Serverul Flask
```

---

## ⚙️ Instalare & Rulare Locală

1. **Clonarea repozitoriului:**
   ```bash

   git clone https://github.com/simonagrama/smart-home-emotional-assistant.git

   cd smart-home-emotional-assistant

   ```

2. **Instalarea dependențelor:**
   ```bash

   pip install -r requirements.txt

   ```

3. **Pornirea serverului Flask:**
   ```bash

   python web_app.py

   ```
   Aplicația va fi accesibilă în browser la adresa http://localhost:5000.

---

## 📽️ Demonstrație Vizuală

<img width="800" height="450" alt="demo" src="https://github.com/user-attachments/assets/1d1c0f7a-52d4-4340-8a00-cbccf0594c21" />

---

## 👤 Autor

* **Simona Grama**

* Facultatea de Inginerie Electrică și Știința Calculatoarelor (IESC)

* Tehnologii și Sisteme de Telecomunicații

* Universitatea Transilvania din Brașov

---
