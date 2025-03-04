`ModuleNotFoundError: No module named 'telegram'` error ka matlab hai ki Telegram ka required module install nahi hai ya phir tum jis environment me run kar rahe ho, wahan module available nahi hai.  

### **Solution Steps:**

#### **1️⃣ Virtual Environment Check & Fix**
Pehle check karo ki virtual environment (`env`) bana hai ya nahi:
```bash
ls
```
Agar `env` folder nahi dikhta, to ek naya virtual environment banao:
```bash
python3 -m venv env
```
Phir usko activate karo:
```bash
source env/bin/activate
```
Ab check karo ki virtual environment sahi activate ho gaya hai ya nahi:
```bash
which python
```
Agar path `/home/ubuntu/insta_auto_upload/env/bin/python` dikhe, to sahi activate ho gaya.

#### **2️⃣ Required Libraries Install Karo**
Agar virtual environment activate ho gaya hai, to required modules install karo:
```bash
pip install python-telegram-bot instagrapi
```
Agar aap `requirements.txt` file use kar rahe ho, to:
```bash
pip install -r requirements.txt
```

#### **3️⃣ Script Dobara Run Karo**
Ab fir se apna script run karo:
```bash
python3 upload_v_1.py
```

Agar fir bhi error aaye to mujhe batao! 🚀

# insta_auto_upload


pip uninstall moviepy
then

pip install moviepy==1.0.3


# Virtual environment activate karein
source telegram-bot-env/bin/activate

# Packages check karein
pip list

# Missing package install karein (agar zaroorat ho)
pip install gdown

# Bot script run karein
python3 insta.py

# Virtual environment deactivate karein
deactivate
