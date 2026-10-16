from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import re
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for demo (works without Firebase)
PATIENTS_DB = [
    # sample records preserved
]

# Read Gemini API key from environment only
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Try to import Gemini - only if API key provided
GEMINI_AVAILABLE = False
if GEMINI_API_KEY:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    except Exception:
        GEMINI_AVAILABLE = False
        print("⚠️  Gemini not available - using fallback extraction")
else:
    print("ℹ️  No GEMINI_API_KEY provided - using fallback extraction")

class TriageEngine:
    def __init__(self):
        self.critical_symptoms = [
            'chest pain', 'shortness of breath', 'acute mi', 'stemi',
            'heart attack', 'stroke', 'seizure', 'unconscious',
            'severe bleeding', 'difficulty breathing', 'cardiac arrest'
        ]

    def classify_patient(self, patient_data):
        risk_factors = self.analyze_risk_factors(patient_data)
        risk_level = self.determine_risk_level(risk_factors, patient_data)
        risk_score = self.calculate_risk_score(risk_factors, patient_data)

        return {
            'riskLevel': risk_level,
            'riskScore': risk_score,
            'riskFactors': risk_factors,
            'recommendations': self.generate_recommendations(risk_level, risk_factors)
        }

    def analyze_risk_factors(self, data):
        factors = {
            'criticalSymptoms': [],
            'vitalSigns': {},
            'allergyConflicts': [],
            'dataCompleteness': {}
        }

        if data.get('symptoms'):
            factors['criticalSymptoms'] = [
                symptom for symptom in data['symptoms']
                if any(critical in symptom.lower() for critical in self.critical_symptoms)
            ]

        factors['vitalSigns'] = self.analyze_vitals(data)
        factors['dataCompleteness'] = self.assess_completeness(data)

        return factors

    def analyze_vitals(self, data):
        vitals = {'bpHigh': False, 'spo2Low': False, 'pulseHigh': False}

        if data.get('bp') and data['bp'] != '0/0':
            bp_match = re.search(r'(\d+)/(\d+)', str(data['bp']))
            if bp_match:
                systolic = int(bp_match.group(1))
                vitals['bpHigh'] = systolic > 160

        if data.get('spo2') and data['spo2'] > 0:
            vitals['spo2Low'] = data['spo2'] < 96

        if data.get('pulse') and data['pulse'] > 0:
            vitals['pulseHigh'] = data['pulse'] > 100

        return vitals

    def assess_completeness(self, data):
        return {
            'hasName': data.get('name') and data['name'] not in ['Unknown Patient', '[Not Provided]', ''],
            'hasAge': data.get('age') and str(data.get('age')) not in ['0', '?', 'Unknown', ''],
            'hasVitals': any([
                data.get('bp') and data['bp'] != '0/0',
                data.get('pulse') and data['pulse'] > 0,
                data.get('spo2') and data['spo2'] > 0
            ]),
            'hasSymptoms': bool(data.get('symptoms'))
        }

    def determine_risk_level(self, factors, patient_data):
        if (factors['criticalSymptoms'] or 
            factors['vitalSigns']['spo2Low'] or 
            factors['vitalSigns']['bpHigh'] or
            (patient_data.get('allergies') and any('aspirin' in str(allergy).lower() for allergy in patient_data['allergies']))):
            return 'CRITICAL'

        completeness = factors['dataCompleteness']
        if (not completeness['hasName'] or 
            not completeness['hasAge'] or 
            not completeness['hasVitals']):
            return 'MODERATE'

        return 'SAFE'

    def calculate_risk_score(self, factors, patient_data):
        score = 0
        score += len(factors['criticalSymptoms']) * 25
        if factors['vitalSigns']['spo2Low']: score += 20
        if factors['vitalSigns']['bpHigh']: score += 15
        if factors['vitalSigns']['pulseHigh']: score += 10

        completeness = factors['dataCompleteness']
        if not completeness['hasName']: score += 15
        if not completeness['hasAge']: score += 15
        if not completeness['hasVitals']: score += 20

        return min(score, 100)

    def generate_recommendations(self, risk_level, factors):
        if risk_level == 'CRITICAL':
            return ['🚨 IMMEDIATE MEDICAL ATTENTION REQUIRED', 'Alert emergency response team', 'Prepare for cardiac intervention']
        elif risk_level == 'MODERATE':
            return ['⚡ Priority triage - see within 30 minutes', 'Complete missing patient information', 'Monitor vital signs']
        else:
            return ['✅ Standard triage process', 'Regular monitoring sufficient']


def extract_patient_data_gemini(raw_text):
    """Extract using Gemini AI (server side only)"""
    if not GEMINI_AVAILABLE:
        return None

    prompt = f"""You are a clinical triage assistant for City General Hospital.

Extract the following fields from the patient intake record provided:
- patientId: found after "PATIENT ID:" 
- name: patient's full name
- age: patient's age (integer, or null if missing)
- symptoms: list of reported symptoms
- allergies: list of known drug or substance allergies  
- medications: current medications with dosage if mentioned
- bp: blood pressure reading (e.g. "180/110")
- pulse: heart rate in bpm
- spo2: oxygen saturation percentage
- doctorNotes: any notes from the attending physician

Return ONLY a valid JSON object. Do not include any explanation, markdown formatting, or extra text.

Patient intake record:
{raw_text}"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        text = response.text

        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return sanitize_data(data)
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


def extract_patient_data_fallback(raw_text):
    """Fallback extraction using regex"""
    data = {
        'patientId': 'PT-000',
        'name': 'Unknown Patient',
        'age': 0,
        'symptoms': [],
        'allergies': [],
        'medications': [],
        'bp': '0/0',
        'pulse': 0,
        'spo2': 0,
        'doctorNotes': ''
    }

    pid_match = re.search(r'PATIENT ID:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if pid_match:
        data['patientId'] = pid_match.group(1).strip()

    name_match = re.search(r'Name:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if name_match:
        data['name'] = name_match.group(1).strip()

    age_match = re.search(r'Age:\s*(\d+)', raw_text, re.IGNORECASE)
    if age_match:
        data['age'] = int(age_match.group(1))

    symptoms_match = re.search(r'Symptoms?:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if symptoms_match:
        data['symptoms'] = [s.strip() for s in symptoms_match.group(1).split(',')]

    allergies_match = re.search(r'(?:Known )?Allergies:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if allergies_match:
        allergy_text = allergies_match.group(1).strip()
        if allergy_text.lower() not in ['none', 'unknown']:
            data['allergies'] = [a.strip() for a in allergy_text.split(',')]

    bp_match = re.search(r'BP:?\s*(\d+/\d+)', raw_text, re.IGNORECASE)
    if bp_match:
        data['bp'] = bp_match.group(1)

    pulse_match = re.search(r'Pulse:?\s*(\d+)', raw_text, re.IGNORECASE)
    if pulse_match:
        data['pulse'] = int(pulse_match.group(1))

    spo2_match = re.search(r'SpO2:?\s*(\d+)', raw_text, re.IGNORECASE)
    if spo2_match:
        data['spo2'] = int(spo2_match.group(1))

    notes_match = re.search(r'Doctor Notes?:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if notes_match:
        data['doctorNotes'] = notes_match.group(1).strip()

    return data


def sanitize_data(data):
    """Sanitize and validate extracted data"""
    return {
        'patientId': data.get('patientId', f'PT-{datetime.now().strftime("%H%M%S")}'),
        'name': data.get('name', 'Unknown Patient'),
        'age': int(data.get('age', 0)) if str(data.get('age', '')).isdigit() else 0,
        'symptoms': data.get('symptoms', []) if isinstance(data.get('symptoms'), list) else [],
        'allergies': data.get('allergies', []) if isinstance(data.get('allergies'), list) else [],
        'medications': data.get('medications', []) if isinstance(data.get('medications'), list) else [],
        'bp': data.get('bp', '0/0'),
        'pulse': int(data.get('pulse', 0)) if str(data.get('pulse', '')).isdigit() else 0,
        'spo2': int(data.get('spo2', 0)) if str(data.get('spo2', '')).isdigit() else 0,
        'doctorNotes': data.get('doctorNotes', '')
    }


def extract_patient_data(raw_text):
    """Main extraction function - prefer server-side Gemini if available"""
    if GEMINI_AVAILABLE:
        data = extract_patient_data_gemini(raw_text)
        if data:
            return data
    return extract_patient_data_fallback(raw_text)

# Initialize triage engine
triage_engine = TriageEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/screen-patient', methods=['POST'])
def screen_patient():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Patient intake text is required'}), 400

        # Extract structured data (server-side)
        extracted_data = extract_patient_data(text)

        # Run triage classification
        triage_result = triage_engine.classify_patient(extracted_data)

        # Prepare patient record
        patient_record = {
            **extracted_data,
            'status': triage_result['riskLevel'],
            'riskScore': triage_result['riskScore'],
            'riskFactors': triage_result['riskFactors'],
            'recommendations': triage_result['recommendations'],
            'rawInput': text,
            'timestamp': datetime.now().isoformat(),
            'processedAt': datetime.now().isoformat(),
            'id': f"patient-{len(PATIENTS_DB) + 1}"
        }

        # Store in memory
        PATIENTS_DB.append(patient_record)

        return jsonify({
            'success': True,
            'patientId': extracted_data['patientId'],
            'firestoreId': patient_record['id'],
            'riskLevel': triage_result['riskLevel'],
            'riskScore': triage_result['riskScore'],
            'recommendations': triage_result['recommendations'],
            'patientData': extracted_data,
            'timestamp': patient_record['processedAt']
        })

    except Exception as e:
        print(f"Error in screen_patient: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        sorted_patients = sorted(PATIENTS_DB, key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({
            'success': True,
            'patients': sorted_patients,
            'count': len(sorted_patients)
        })
    except Exception as e:
        print(f"Error in get_patients: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = {
            'totalPatients': len(PATIENTS_DB),
            'riskLevels': {'CRITICAL': 0, 'MODERATE': 0, 'SAFE': 0},
            'averageRiskScore': 0
        }

        total_risk_score = 0
        for patient in PATIENTS_DB:
            if patient.get('status'):
                stats['riskLevels'][patient['status']] += 1
            if patient.get('riskScore'):
                total_risk_score += patient['riskScore']

        if stats['totalPatients'] > 0:
            stats['averageRiskScore'] = round(total_risk_score / stats['totalPatients'])

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏥 MedGuard AI Starting...")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("🔬 Main App: http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
