# SecureGait

SecureGait is an intelligent, automated access control system that uses gait recognition to identify and authorize people based on their walking patterns. This project combines hardware (Raspberry Pi, DAQ card, laser-beam sensors), software (Python, LabVIEW), machine learning (Random Forest), and cloud integration (Firebase) to deliver a secure, contactless entry system.

---

## 🚀 Features

- **Real-time Gait-Based Identification**  
  Recognizes people by analyzing their walking pattern using a trained ML model.

- **Automated Video Capture**  
  Raspberry Pi records video on sensor trigger, runs classification automatically.

- **Machine Learning Classification**  
  Random Forest model (pickle) predicts authorized vs. unauthorized users.

- **Access Control Actions**  
  - Opens gate for authorized users.
  - Sounds buzzer for unauthorized users.

- **Live Database and Web Integration**  
  - Uses Firebase for real-time updates.
  - Admin web interface to approve or reject users.
  - Blocks entry for rejected or unknown users.

---

## ⚙️ System Architecture

1. **Sensing and Trigger**  
   - Laser-beam sensor detects crossing.
   - DAQ card captures signal.
   - LabVIEW sends signal to Raspberry Pi.

2. **Video Recording and Processing**  
   - Raspberry Pi runs `test.py` as a background service.
   - On trigger, records video for gait analysis.

3. **Machine Learning Model**  
   - Pre-trained Random Forest model loaded via pickle.
   - Predicts if the person is authorized.

4. **Access Decision**  
   - If authorized: Gate opens.
   - If unauthorized: Buzzer sounds.

5. **Database and Website**  
   - Firebase stores detection logs.
   - Website shows live updates.
   - Admin can approve/reject users in real time.

---

## 🛠️ Technologies Used

- **Hardware**  
  - Raspberry Pi  
  - DAQ Card  
  - Laser-beam sensor

- **Software & Programming**  
  - Python (background service, video recording, ML prediction)
  - LabVIEW (DAQ integration)
  - Random Forest ML model (pickle)
  - Firebase (Realtime Database)
  - Web front-end (for admin approval)

---

## 📸 Demo / Screenshots

*(Add images or GIFs of your hardware setup, web interface, flow diagram, etc. here)*

---

## 🌐 How It Works

> 1️⃣ Person crosses laser beam →  
> 2️⃣ DAQ card sends trigger →  
> 3️⃣ Raspberry Pi records video →  
> 4️⃣ ML model predicts authorization →  
> 5️⃣ Gate opens or buzzer sounds →  
> 6️⃣ Firebase updates logs →  
> 7️⃣ Admin manages approvals on website

---


