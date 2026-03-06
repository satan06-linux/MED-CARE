from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for demo (works without Firebase)
PATIENTS_DB = [
    {
        'id': 'patient-1',
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
        'riskFactors': {
            'criticalSymptoms': ['severe chest pain', 'shortness of breath'],
            'vitalSigns': {'bpHigh': True, 'spo2Low': True, 'pulseHigh': True},
            'allergyConflicts': [],
            'dataCompleteness': {'hasName': True, 'hasAge': True, 'hasVitals': True, 'hasSymptoms': True}
        },
        'recommendations': ['🚨 IMMEDIATE MEDICAL ATTENTION REQUIRED', 'Alert emergency response team', 'Prepare for cardiac intervention'],
        'rawInput': 'PATIENT ID: PT-001\nName: Ravi Shankar\nAge: 58\nSymptoms: Severe chest pain, shortness of breath\nAllergies: Penicillin, Aspirin\nBP: 180/110\nPulse: 102\nSpO2: 94%',
        'timestamp': datetime.now().isoformat(),
        'processedAt': datetime.now().isoformat()
    },
    {
        'id': 'patient-2',
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
        'riskFactors': {
            'criticalSymptoms': [],
            'vitalSigns': {'bpHigh': False, 'spo2Low': False, 'pulseHigh': False},
            'allergyConflicts': [],
            'dataCompleteness': {'hasName': True, 'hasAge': True, 'hasVitals': True, 'hasSymptoms': True}
        },
        'recommendations': ['✅ Standard triage process', 'Regular monitoring sufficient'],
        'rawInput': 'PATIENT ID: PT-002\nName: Priya Mehta\nAge: 29\nSymptoms: Mild seasonal cough, runny nose\nBP: 118/76\nPulse: 72\nSpO2: 99%',
        'timestamp': datetime.now().isoformat(),
        'processedAt': datetime.now().isoformat()
    },
    {
        'id': 'patient-3',
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
        'riskFactors': {
            'criticalSymptoms': [],
            'vitalSigns': {'bpHigh': False, 'spo2Low': False, 'pulseHigh': False},
            'allergyConflicts': [],
            'dataCompleteness': {'hasName': False, 'hasAge': False, 'hasVitals': False, 'hasSymptoms': True}
        },
        'recommendations': ['⚡ Priority triage - see within 30 minutes', 'Complete missing patient information', 'Monitor vital signs'],
        'rawInput': 'PATIENT ID: PT-003\nName: [Not Provided]\nAge: ?\nSymptoms: Dizziness and some pain\nVitals: Not recorded',
        'timestamp': datetime.now().isoformat(),
        'processedAt': datetime.now().isoformat()
    },
    {
        'id': 'patient-4',
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
        'riskFactors': {
            'criticalSymptoms': [],
            'vitalSigns': {'bpHigh': False, 'spo2Low': False, 'pulseHigh': False},
            'allergyConflicts': [],
            'dataCompleteness': {'hasName': True, 'hasAge': True, 'hasVitals': True, 'hasSymptoms': True}
        },
        'recommendations': ['✅ Standard triage process', 'Regular monitoring sufficient'],
        'rawInput': 'PATIENT ID: PT-004\nName: Amit Kumar\nAge: 42\nSymptoms: fever, body ache, headache\nBP: 125/82\nPulse: 88\nSpO2: 98%',
        'timestamp': datetime.now().isoformat(),
        'processedAt': datetime.now().isoformat()
    },
    {
        'id': 'patient-5',
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
        'riskFactors': {
            'criticalSymptoms': ['difficulty breathing'],
            'vitalSigns': {'bpHigh': True, 'spo2Low': True, 'pulseHigh': False},
            'allergyConflicts': [],
            'dataCompleteness': {'hasName': True, 'hasAge': True, 'hasVitals': True, 'hasSymptoms': True}
        },
        'recommendations': ['🚨 IMMEDIATE MEDICAL ATTENTION REQUIRED', 'Alert emergency response team', 'Prepare for cardiac intervention'],
        'rawInput': 'PATIENT ID: PT-005\nName: Sarah Johnson\nAge: 65\nSymptoms: difficulty breathing, wheezing\nAllergies: Sulfa drugs\nBP: 165/95\nPulse: 98\nSpO2: 92%',
        'timestamp': datetime.now().isoformat(),
        'processedAt': datetime.now().isoformat()
    }
]

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyDkFRAgQ1gRuKaKjJDPKj7Udf2B_xXyBfs"

# Try to import Gemini - fallback if not available
try:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not available - using fallback extraction")

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
    """Extract using Gemini AI"""
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
        return extract_patient_data_fallback(raw_text)

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
    
    # Extract patient ID
    pid_match = re.search(r'PATIENT ID:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if pid_match:
        data['patientId'] = pid_match.group(1).strip()
    
    # Extract name
    name_match = re.search(r'Name:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if name_match:
        data['name'] = name_match.group(1).strip()
    
    # Extract age
    age_match = re.search(r'Age:\s*(\d+)', raw_text, re.IGNORECASE)
    if age_match:
        data['age'] = int(age_match.group(1))
    
    # Extract symptoms
    symptoms_match = re.search(r'Symptoms?:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if symptoms_match:
        data['symptoms'] = [s.strip() for s in symptoms_match.group(1).split(',')]
    
    # Extract allergies
    allergies_match = re.search(r'(?:Known )?Allergies:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if allergies_match:
        allergy_text = allergies_match.group(1).strip()
        if allergy_text.lower() not in ['none', 'unknown']:
            data['allergies'] = [a.strip() for a in allergy_text.split(',')]
    
    # Extract BP
    bp_match = re.search(r'BP:?\s*(\d+/\d+)', raw_text, re.IGNORECASE)
    if bp_match:
        data['bp'] = bp_match.group(1)
    
    # Extract pulse
    pulse_match = re.search(r'Pulse:?\s*(\d+)', raw_text, re.IGNORECASE)
    if pulse_match:
        data['pulse'] = int(pulse_match.group(1))
    
    # Extract SpO2
    spo2_match = re.search(r'SpO2:?\s*(\d+)', raw_text, re.IGNORECASE)
    if spo2_match:
        data['spo2'] = int(spo2_match.group(1))
    
    # Extract doctor notes
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
    """Main extraction function"""
    if GEMINI_AVAILABLE:
        return extract_patient_data_gemini(raw_text)
    else:
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
        
        # Extract structured data
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
        # Return patients sorted by timestamp (newest first)
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
    app.run(debug=True, host='0.0.0.0', port=5000)
