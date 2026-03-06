const { GoogleGenerativeAI } = require('@google/generative-ai');
const { extractJSON } = require('./utils/jsonParser');

class LLMExtractor {
  constructor() {
    this.genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-pro" });
  }

  /**
   * Extract structured medical data from raw intake text using Gemini AI
   * @param {string} rawText - Raw patient intake text
   * @returns {Promise<Object>} Structured patient data
   */
  async extractPatientData(rawText) {
    try {
      const prompt = `
You are a medical data extraction AI. Extract structured information from the following patient intake record.

IMPORTANT: Return ONLY valid JSON with no markdown, no explanations, no extra text.

Required fields:
- patientId: string (extract from text or generate PT-XXX format)
- name: string (patient full name)
- age: number (patient age)
- symptoms: array of strings (list all symptoms mentioned)
- allergies: array of strings (list all allergies, empty array if none)
- medications: array of strings (list all medications, empty array if none)
- bp: string (blood pressure reading like "120/80")
- pulse: number (heart rate)
- spo2: number (oxygen saturation percentage)
- doctorNotes: string (any doctor notes or observations)

If any field is missing or unclear, use these defaults:
- patientId: generate "PT-" + random 3 digits
- name: "Unknown Patient"
- age: 0
- symptoms: []
- allergies: []
- medications: []
- bp: "0/0"
- pulse: 0
- spo2: 0
- doctorNotes: ""

Patient intake record:
${rawText}

Return only the JSON object:`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      // Extract JSON from response (handles markdown or extra text)
      const extractedData = extractJSON(text);
      
      // Validate and sanitize the extracted data
      return this.validateAndSanitize(extractedData);

    } catch (error) {
      console.error('LLM Extraction Error:', error);
      throw new Error(`Failed to extract patient data: ${error.message}`);
    }
  }

  /**
   * Validate and sanitize extracted patient data
   * @param {Object} data - Raw extracted data
   * @returns {Object} Validated and sanitized data
   */
  validateAndSanitize(data) {
    const sanitized = {
      patientId: data.patientId || `PT-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      name: data.name || 'Unknown Patient',
      age: parseInt(data.age) || 0,
      symptoms: Array.isArray(data.symptoms) ? data.symptoms : [],
      allergies: Array.isArray(data.allergies) ? data.allergies : [],
      medications: Array.isArray(data.medications) ? data.medications : [],
      bp: data.bp || '0/0',
      pulse: parseInt(data.pulse) || 0,
      spo2: parseInt(data.spo2) || 0,
      doctorNotes: data.doctorNotes || ''
    };

    // Normalize symptoms and allergies to lowercase for consistency
    sanitized.symptoms = sanitized.symptoms.map(s => s.toLowerCase().trim());
    sanitized.allergies = sanitized.allergies.map(a => a.toLowerCase().trim());

    return sanitized;
  }

  /**
   * Test the LLM extraction with sample data
   * @returns {Promise<Object>} Test result
   */
  async testExtraction() {
    const sampleText = `
PATIENT ID: PT-001
Name: Ravi Shankar
Age: 58
Symptoms: chest pain, shortness of breath
Allergies: Penicillin
BP: 180/110
Pulse: 102
SpO2: 94%
Doctor Notes: Possible acute MI. Do NOT administer aspirin.
    `;

    try {
      const result = await this.extractPatientData(sampleText);
      console.log('✅ LLM Extraction Test Successful:', result);
      return result;
    } catch (error) {
      console.error('❌ LLM Extraction Test Failed:', error);
      throw error;
    }
  }
}

module.exports = LLMExtractor;