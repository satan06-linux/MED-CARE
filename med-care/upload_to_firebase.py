"""
Upload Example Patient Data to Firebase Firestore
Run this script to populate your Firebase database with test data
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase with your project
# You need to download the service account key from Firebase Console
# Go to: Project Settings > Service Accounts > Generate New Private Key

# Option 1: Use service account JSON file (recommended)
# Download the JSON file and save it as 'serviceAccountKey.json'
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    print("✅ Firebase initialized with service account")
except:
    print("❌ Service account file not found")
    print("\n📋 To get your service account key:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Select project: med-care-f2d63")
    print("3. Go to Project Settings > Service Accounts")
    print("4. Click 'Generate New Private Key'")
    print("5. Save the file as 'serviceAccountKey.json' in this folder")
    print("\nOr use the web configuration below:")
    print("\n" + "="*60)
    print("FIREBASE WEB CONFIG (for frontend):")
    print("="*60)
    print("""
const firebaseConfig = {
  apiKey: "AIzaSyDtawLZb3XTIhc3oaDNK4Kg0K5D2vioAUM",
  authDomain: "med-care-f2d63.firebaseapp.com",
  projectId: "med-care-f2d63",
  storageBucket: "med-care-f2d63.firebasestorage.app",
  messagingSenderId: "360190835550",
  appId: "1:360190835550:web:436f8e99f6a929f7a92dcf",
  measurementId: "G-NJGEL2Q2GW"
};
    """)
    exit(1)

db = firestore.client()

# Example patient data
patients = [
    {
        'patientId': 'PT-001',
        'name': 'Ravi Shankar',
        'age': 58,
        'symptoms': ['severe chest pain', 'shortness of breath', 'radiating pain to left arm'],
        'allergies': ['Penicillin', 'Aspirin'],
        'medications': ['Warfarin 5mg daily'],
        'bp': '180/110',
        'pulse': 102,
        'spo2': 94,
        'doctorNotes': 'Possible acute MI. Rule out STEMI. Do NOT administer aspirin.',
        'status': 'CRITICAL',
        'riskScore': 85,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'processedAt': datetime.now().isoformat()
    },
    {
        'patientId': 'PT-002',
        'name': 'Priya Mehta',
        'age': 29,
        'symptoms': ['mild seasonal cough', 'runny nose for 3 days'],
        'allergies': [],
        'medications': [],
        'bp': '118/76',
        'pulse': 72,
        'spo2': 99,
        'doctorNotes': 'Likely viral URI. Prescribed antihistamines.',
        'status': 'SAFE',
        'riskScore': 0,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'processedAt': datetime.now().isoformat()
    },
    {
        'patientId': 'PT-003',
        'name': 'Unknown Patient',
        'age': 0,
        'symptoms': ['dizziness', 'some pain'],
        'allergies': [],
        'medications': [],
        'bp': '0/0',
        'pulse': 0,
        'spo2': 0,
        'doctorNotes': 'Patient brought in by bystander. Unresponsive on arrival.',
        'status': 'MODERATE',
        'riskScore': 50,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'processedAt': datetime.now().isoformat()
    },
    {
        'patientId': 'PT-004',
        'name': 'Amit Kumar',
        'age': 42,
        'symptoms': ['fever', 'body ache', 'headache'],
        'allergies': [],
        'medications': ['Paracetamol 500mg'],
        'bp': '125/82',
        'pulse': 88,
        'spo2': 98,
        'doctorNotes': 'Viral fever. Rest and hydration advised.',
        'status': 'SAFE',
        'riskScore': 5,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'processedAt': datetime.now().isoformat()
    },
    {
        'patientId': 'PT-005',
        'name': 'Sarah Johnson',
        'age': 65,
        'symptoms': ['difficulty breathing', 'wheezing'],
        'allergies': ['Sulfa drugs'],
        'medications': ['Albuterol inhaler'],
        'bp': '165/95',
        'pulse': 98,
        'spo2': 92,
        'doctorNotes': 'Acute asthma exacerbation. Nebulization started.',
        'status': 'CRITICAL',
        'riskScore': 70,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'processedAt': datetime.now().isoformat()
    }
]

print("\n🔥 Uploading patients to Firebase Firestore...")
print("="*60)

for patient in patients:
    try:
        # Add to 'patients' collection
        doc_ref = db.collection('patients').add(patient)
        print(f"✅ Added {patient['patientId']}: {patient['name']} ({patient['status']})")
    except Exception as e:
        print(f"❌ Error adding {patient['patientId']}: {e}")

print("="*60)
print("✅ Upload complete!")
print("\n📊 Check your Firebase Console:")
print("https://console.firebase.google.com/project/med-care-f2d63/firestore")
print("\nYou should see 5 patients in the 'patients' collection")
