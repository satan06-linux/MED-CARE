class TriageEngine {
  constructor() {
    this.riskLevels = {
      CRITICAL: 'CRITICAL',
      MODERATE: 'MODERATE',
      SAFE: 'SAFE'
    };

    // Critical symptoms that require immediate attention
    this.criticalSymptoms = [
      'chest pain',
      'shortness of breath',
      'acute mi',
      'stemi',
      'heart attack',
      'stroke',
      'seizure',
      'unconscious',
      'severe bleeding',
      'difficulty breathing',
      'cardiac arrest'
    ];

    // Dangerous allergies that can cause severe reactions
    this.dangerousAllergies = [
      'penicillin',
      'aspirin',
      'latex',
      'shellfish',
      'nuts',
      'bee stings',
      'contrast dye'
    ];
  }

  /**
   * Classify patient risk level based on extracted medical data
   * @param {Object} patientData - Structured patient data
   * @returns {Object} Triage result with risk level and score
   */
  classifyPatient(patientData) {
    try {
      const riskFactors = this.analyzeRiskFactors(patientData);
      const riskLevel = this.determineRiskLevel(riskFactors);
      const riskScore = this.calculateRiskScore(riskFactors);

      return {
        riskLevel,
        riskScore,
        riskFactors,
        recommendations: this.generateRecommendations(riskLevel, riskFactors),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Triage Classification Error:', error);
      throw new Error(`Failed to classify patient: ${error.message}`);
    }
  }

  /**
   * Analyze various risk factors from patient data
   * @param {Object} patientData - Patient medical data
   * @returns {Object} Risk factors analysis
   */
  analyzeRiskFactors(patientData) {
    const factors = {
      criticalSymptoms: [],
      vitalSigns: {},
      allergyConflicts: [],
      dataCompleteness: {},
      ageRisk: false
    };

    // Check for critical symptoms
    if (patientData.symptoms && Array.isArray(patientData.symptoms)) {
      factors.criticalSymptoms = patientData.symptoms.filter(symptom =>
        this.criticalSymptoms.some(critical => 
          symptom.toLowerCase().includes(critical)
        )
      );
    }

    // Analyze vital signs
    factors.vitalSigns = this.analyzeVitalSigns(patientData);

    // Check for dangerous allergy conflicts
    if (patientData.allergies && Array.isArray(patientData.allergies)) {
      factors.allergyConflicts = patientData.allergies.filter(allergy =>
        this.dangerousAllergies.some(dangerous =>
          allergy.toLowerCase().includes(dangerous)
        )
      );
    }

    // Assess data completeness
    factors.dataCompleteness = this.assessDataCompleteness(patientData);

    // Age-based risk (elderly patients)
    factors.ageRisk = patientData.age > 65;

    return factors;
  }

  /**
   * Analyze vital signs for abnormal values
   * @param {Object} patientData - Patient data
   * @returns {Object} Vital signs analysis
   */
  analyzeVitalSigns(patientData) {
    const vitals = {
      bpHigh: false,
      bpLow: false,
      pulseHigh: false,
      pulseLow: false,
      spo2Low: false,
      normalVitals: true
    };

    // Blood pressure analysis
    if (patientData.bp && patientData.bp !== '0/0') {
      const bpMatch = patientData.bp.match(/(\d+)\/(\d+)/);
      if (bpMatch) {
        const systolic = parseInt(bpMatch[1]);
        const diastolic = parseInt(bpMatch[2]);
        
        vitals.bpHigh = systolic > 160 || diastolic > 100;
        vitals.bpLow = systolic < 90 || diastolic < 60;
        
        if (vitals.bpHigh || vitals.bpLow) vitals.normalVitals = false;
      }
    }

    // Pulse analysis
    if (patientData.pulse && patientData.pulse > 0) {
      vitals.pulseHigh = patientData.pulse > 100;
      vitals.pulseLow = patientData.pulse < 60;
      
      if (vitals.pulseHigh || vitals.pulseLow) vitals.normalVitals = false;
    }

    // SpO2 analysis
    if (patientData.spo2 && patientData.spo2 > 0) {
      vitals.spo2Low = patientData.spo2 < 96;
      
      if (vitals.spo2Low) vitals.normalVitals = false;
    }

    return vitals;
  }

  /**
   * Assess completeness of patient data
   * @param {Object} patientData - Patient data
   * @returns {Object} Data completeness assessment
   */
  assessDataCompleteness(patientData) {
    const completeness = {
      hasName: patientData.name && patientData.name !== 'Unknown Patient',
      hasAge: patientData.age && patientData.age > 0,
      hasVitals: patientData.bp !== '0/0' || patientData.pulse > 0 || patientData.spo2 > 0,
      hasSymptoms: patientData.symptoms && patientData.symptoms.length > 0,
      complete: true
    };

    completeness.complete = completeness.hasName && completeness.hasAge && 
                           completeness.hasVitals && completeness.hasSymptoms;

    return completeness;
  }

  /**
   * Determine overall risk level based on risk factors
   * @param {Object} riskFactors - Analyzed risk factors
   * @returns {string} Risk level (CRITICAL, MODERATE, SAFE)
   */
  determineRiskLevel(riskFactors) {
    // CRITICAL conditions
    if (riskFactors.criticalSymptoms.length > 0 ||
        riskFactors.vitalSigns.spo2Low ||
        riskFactors.vitalSigns.bpHigh ||
        (riskFactors.allergyConflicts.length > 0 && riskFactors.criticalSymptoms.length > 0)) {
      return this.riskLevels.CRITICAL;
    }

    // MODERATE conditions
    if (!riskFactors.dataCompleteness.complete ||
        !riskFactors.dataCompleteness.hasName ||
        !riskFactors.dataCompleteness.hasAge ||
        !riskFactors.dataCompleteness.hasVitals ||
        riskFactors.vitalSigns.pulseHigh ||
        riskFactors.vitalSigns.pulseLow ||
        riskFactors.allergyConflicts.length > 0) {
      return this.riskLevels.MODERATE;
    }

    // SAFE conditions
    return this.riskLevels.SAFE;
  }

  /**
   * Calculate numerical risk score (0-100)
   * @param {Object} riskFactors - Risk factors analysis
   * @returns {number} Risk score
   */
  calculateRiskScore(riskFactors) {
    let score = 0;

    // Critical symptoms (40 points max)
    score += riskFactors.criticalSymptoms.length * 20;
    score = Math.min(score, 40);

    // Vital signs (30 points max)
    if (riskFactors.vitalSigns.spo2Low) score += 15;
    if (riskFactors.vitalSigns.bpHigh) score += 10;
    if (riskFactors.vitalSigns.pulseHigh || riskFactors.vitalSigns.pulseLow) score += 5;

    // Allergy conflicts (15 points max)
    score += Math.min(riskFactors.allergyConflicts.length * 5, 15);

    // Data incompleteness (10 points max)
    if (!riskFactors.dataCompleteness.complete) score += 10;

    // Age risk (5 points max)
    if (riskFactors.ageRisk) score += 5;

    return Math.min(score, 100);
  }

  /**
   * Generate recommendations based on risk level and factors
   * @param {string} riskLevel - Patient risk level
   * @param {Object} riskFactors - Risk factors
   * @returns {Array} Array of recommendations
   */
  generateRecommendations(riskLevel, riskFactors) {
    const recommendations = [];

    switch (riskLevel) {
      case this.riskLevels.CRITICAL:
        recommendations.push('🚨 IMMEDIATE MEDICAL ATTENTION REQUIRED');
        recommendations.push('Alert emergency response team');
        recommendations.push('Prepare for potential cardiac intervention');
        if (riskFactors.allergyConflicts.length > 0) {
          recommendations.push('⚠️ Check allergy conflicts before medication');
        }
        break;

      case this.riskLevels.MODERATE:
        recommendations.push('⚡ Priority triage - see within 30 minutes');
        recommendations.push('Monitor vital signs closely');
        if (!riskFactors.dataCompleteness.complete) {
          recommendations.push('Complete missing patient information');
        }
        break;

      case this.riskLevels.SAFE:
        recommendations.push('✅ Standard triage process');
        recommendations.push('Regular monitoring sufficient');
        break;
    }

    return recommendations;
  }

  /**
   * Test the triage engine with sample data
   * @returns {Object} Test result
   */
  testTriage() {
    const samplePatient = {
      patientId: 'PT-001',
      name: 'Ravi Shankar',
      age: 58,
      symptoms: ['chest pain', 'shortness of breath'],
      allergies: ['penicillin'],
      medications: [],
      bp: '180/110',
      pulse: 102,
      spo2: 94,
      doctorNotes: 'Possible acute MI'
    };

    try {
      const result = this.classifyPatient(samplePatient);
      console.log('✅ Triage Engine Test Successful:', result);
      return result;
    } catch (error) {
      console.error('❌ Triage Engine Test Failed:', error);
      throw error;
    }
  }
}

module.exports = TriageEngine;