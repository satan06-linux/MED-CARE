# 🔥 Firebase Setup Guide - MedGuard AI

## Quick Setup (5 Minutes)

### Step 1: Get Your Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **med-care-f2d63**
3. Click the ⚙️ gear icon → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **"Generate New Private Key"** button
6. Download the JSON file
7. Save it as `serviceAccountKey.json` in your project folder

### Step 2: Enable Firestore Database

1. In Firebase Console, go to **Firestore Database**
2. Click **"Create Database"**
3. Choose **"Start in test mode"** (for hackathon)
4. Select location: **us-central** (or closest to you)
5. Click **"Enable"**

### Step 3: Upload Example Data

```bash
# Install Firebase Admin SDK
pip install firebase-admin

# Run the upload script
python upload_to_firebase.py
```

### Step 4: Verify Data

1. Go to Firebase Console → Firestore Database
2. You should see a collection called **"patients"**
3. It should contain 5 documents (PT-001 through PT-005)

---

## 🎯 Your Firebase Project Details

**Project ID:** med-care-f2d63  
**Project Name:** med-care  

**Web Config (Already in your code):**
```javascript
apiKey: "AIzaSyDtawLZb3XTIhc3oaDNK4Kg0K5D2vioAUM"
authDomain: "med-care-f2d63.firebaseapp.com"
projectId: "med-care-f2d63"
storageBucket: "med-care-f2d63.firebasestorage.app"
messagingSenderId: "360190835550"
appId: "1:360190835550:web:436f8e99f6a929f7a92dcf"
```

---

## 📊 Example Data That Will Be Uploaded

### PT-001 - CRITICAL ⚠️
- **Name:** Ravi Shankar (58 years)
- **Symptoms:** Chest pain, shortness of breath
- **Vitals:** BP 180/110, Pulse 102, SpO2 94%
- **Allergies:** Penicillin, Aspirin
- **Risk Score:** 85/100

### PT-002 - SAFE ✅
- **Name:** Priya Mehta (29 years)
- **Symptoms:** Mild cough, runny nose
- **Vitals:** BP 118/76, Pulse 72, SpO2 99%
- **Risk Score:** 0/100

### PT-003 - MODERATE ⚡
- **Name:** Unknown Patient
- **Symptoms:** Dizziness, pain
- **Vitals:** Not recorded
- **Risk Score:** 50/100

### PT-004 - SAFE ✅
- **Name:** Amit Kumar (42 years)
- **Symptoms:** Fever, body ache
- **Vitals:** BP 125/82, Pulse 88, SpO2 98%
- **Risk Score:** 5/100

### PT-005 - CRITICAL ⚠️
- **Name:** Sarah Johnson (65 years)
- **Symptoms:** Difficulty breathing, wheezing
- **Vitals:** BP 165/95, Pulse 98, SpO2 92%
- **Allergies:** Sulfa drugs
- **Risk Score:** 70/100

---

## 🔧 Firestore Security Rules (For Hackathon)

In Firebase Console → Firestore Database → Rules, use:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;  // Open for hackathon demo
    }
  }
}
```

⚠️ **Note:** This is for hackathon only! In production, use proper security rules.

---

## 🚀 After Setup

Your app will automatically:
- ✅ Store new patients in Firestore
- ✅ Retrieve patients from Firestore
- ✅ Update stats in real-time
- ✅ Persist data even after server restart

---

## 🆘 Troubleshooting

### Error: "Default credentials not found"
- Make sure `serviceAccountKey.json` is in the project folder
- Check the file name is exactly `serviceAccountKey.json`

### Error: "Permission denied"
- Go to Firestore Rules and set to test mode
- Make sure Firestore is enabled in your project

### Can't find the project
- Project ID: **med-care-f2d63**
- Make sure you're logged into the correct Google account

---

## 📱 Quick Links

- [Firebase Console](https://console.firebase.google.com/project/med-care-f2d63)
- [Firestore Database](https://console.firebase.google.com/project/med-care-f2d63/firestore)
- [Project Settings](https://console.firebase.google.com/project/med-care-f2d63/settings/general)

---

**Need help? The app works perfectly with in-memory storage for the hackathon demo!**
