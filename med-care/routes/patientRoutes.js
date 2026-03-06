const express = require('express');
const { db } = require('../firebase');
const LLMExtractor = require('../llmExtractor');
const TriageEngine = require('../triageEngine');

const router = express.Router();
const llmExtractor = new LLMExtractor();
const triageEngine = new TriageEngine();

/**
 * POST /screen-patient
 * Main endpoint for patient intake screening
 */
router.post('/screen-patient', async (req, res) => {
  try {
    const { text } = req.body;

    // Validate input
    if (!text || typeof text !== 'string' || text.trim().length === 0) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Patient intake text is required and must be a non-empty string'
      });
    }

    console.log('🏥 Processing patient intake:', text.substring(0, 100) + '...');

    // Step 1: Extract structured data using LLM
    const extractedData = await llmExtractor.extractPatientData(text);
    console.log('📊 Extracted data:', extractedData);

    // Step 2: Run triage classification
    const triageResult = triageEngine.classifyPatient(extractedData);
    console.log('🚨 Triage result:', triageResult);

    // Step 3: Prepare complete patient record
    const patientRecord = {
      ...extractedData,
      status: triageResult.riskLevel,
      riskScore: triageResult.riskScore,
      riskFactors: triageResult.riskFactors,
      recommendations: triageResult.recommendations,
      rawInput: text,
      timestamp: new Date(),
      processedAt: new Date().toISOString()
    };

    // Step 4: Store in Firestore
    const docRef = await db.collection('patients').add(patientRecord);
    console.log('💾 Stored patient record with ID:', docRef.id);

    // Step 5: Return structured result
    const response = {
      success: true,
      patientId: extractedData.patientId,
      firestoreId: docRef.id,
      riskLevel: triageResult.riskLevel,
      riskScore: triageResult.riskScore,
      recommendations: triageResult.recommendations,
      patientData: extractedData,
      triageDetails: triageResult,
      timestamp: patientRecord.processedAt
    };

    res.status(200).json(response);

  } catch (error) {
    console.error('❌ Patient screening error:', error);
    
    // Determine appropriate error response
    let statusCode = 500;
    let errorMessage = 'Internal server error during patient screening';

    if (error.message.includes('Failed to extract patient data')) {
      statusCode = 422;
      errorMessage = 'Unable to process patient intake text with AI';
    } else if (error.message.includes('Failed to classify patient')) {
      statusCode = 422;
      errorMessage = 'Unable to perform medical triage classification';
    }

    res.status(statusCode).json({
      error: 'Processing Failed',
      message: errorMessage,
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * GET /patients
 * Retrieve all patients sorted by timestamp
 */
router.get('/patients', async (req, res) => {
  try {
    console.log('📋 Retrieving all patients...');

    // Query Firestore for all patients, ordered by timestamp (newest first)
    const snapshot = await db.collection('patients')
      .orderBy('timestamp', 'desc')
      .get();

    if (snapshot.empty) {
      return res.status(200).json({
        success: true,
        patients: [],
        count: 0,
        message: 'No patients found'
      });
    }

    // Transform Firestore documents to JSON
    const patients = [];
    snapshot.forEach(doc => {
      const data = doc.data();
      patients.push({
        id: doc.id,
        ...data,
        timestamp: data.timestamp?.toDate?.() || data.timestamp
      });
    });

    console.log(`📊 Retrieved ${patients.length} patients`);

    res.status(200).json({
      success: true,
      patients,
      count: patients.length,
      retrievedAt: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Error retrieving patients:', error);
    
    res.status(500).json({
      error: 'Database Error',
      message: 'Failed to retrieve patient records',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * GET /patients/:id
 * Retrieve a specific patient by ID
 */
router.get('/patients/:id', async (req, res) => {
  try {
    const { id } = req.params;

    if (!id) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Patient ID is required'
      });
    }

    console.log('🔍 Retrieving patient:', id);

    const doc = await db.collection('patients').doc(id).get();

    if (!doc.exists) {
      return res.status(404).json({
        error: 'Not Found',
        message: 'Patient not found'
      });
    }

    const patientData = doc.data();
    const patient = {
      id: doc.id,
      ...patientData,
      timestamp: patientData.timestamp?.toDate?.() || patientData.timestamp
    };

    res.status(200).json({
      success: true,
      patient,
      retrievedAt: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Error retrieving patient:', error);
    
    res.status(500).json({
      error: 'Database Error',
      message: 'Failed to retrieve patient record',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * GET /stats
 * Get system statistics and health metrics
 */
router.get('/stats', async (req, res) => {
  try {
    console.log('📈 Generating system statistics...');

    // Get patient counts by risk level
    const snapshot = await db.collection('patients').get();
    
    const stats = {
      totalPatients: snapshot.size,
      riskLevels: {
        CRITICAL: 0,
        MODERATE: 0,
        SAFE: 0
      },
      averageRiskScore: 0,
      lastProcessed: null
    };

    let totalRiskScore = 0;
    let latestTimestamp = null;

    snapshot.forEach(doc => {
      const data = doc.data();
      
      // Count by risk level
      if (data.status) {
        stats.riskLevels[data.status] = (stats.riskLevels[data.status] || 0) + 1;
      }
      
      // Sum risk scores
      if (data.riskScore) {
        totalRiskScore += data.riskScore;
      }
      
      // Track latest timestamp
      const timestamp = data.timestamp?.toDate?.() || new Date(data.timestamp);
      if (!latestTimestamp || timestamp > latestTimestamp) {
        latestTimestamp = timestamp;
      }
    });

    // Calculate average risk score
    if (stats.totalPatients > 0) {
      stats.averageRiskScore = Math.round(totalRiskScore / stats.totalPatients);
    }

    stats.lastProcessed = latestTimestamp;

    res.status(200).json({
      success: true,
      stats,
      generatedAt: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Error generating stats:', error);
    
    res.status(500).json({
      error: 'Database Error',
      message: 'Failed to generate system statistics',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * POST /test
 * Test endpoint for system validation
 */
router.post('/test', async (req, res) => {
  try {
    console.log('🧪 Running system tests...');

    const testResults = {
      llmExtraction: null,
      triageEngine: null,
      firestore: null,
      timestamp: new Date().toISOString()
    };

    // Test LLM Extraction
    try {
      testResults.llmExtraction = await llmExtractor.testExtraction();
      testResults.llmExtraction.status = 'PASSED';
    } catch (error) {
      testResults.llmExtraction = { status: 'FAILED', error: error.message };
    }

    // Test Triage Engine
    try {
      testResults.triageEngine = triageEngine.testTriage();
      testResults.triageEngine.status = 'PASSED';
    } catch (error) {
      testResults.triageEngine = { status: 'FAILED', error: error.message };
    }

    // Test Firestore Connection
    try {
      await db.collection('test').doc('connection').set({ 
        test: true, 
        timestamp: new Date() 
      });
      await db.collection('test').doc('connection').delete();
      testResults.firestore = { status: 'PASSED', message: 'Connection successful' };
    } catch (error) {
      testResults.firestore = { status: 'FAILED', error: error.message };
    }

    const allPassed = Object.values(testResults).every(result => 
      result && result.status === 'PASSED'
    );

    res.status(allPassed ? 200 : 500).json({
      success: allPassed,
      message: allPassed ? 'All tests passed' : 'Some tests failed',
      results: testResults
    });

  } catch (error) {
    console.error('❌ Test execution error:', error);
    
    res.status(500).json({
      error: 'Test Error',
      message: 'Failed to execute system tests',
      details: error.message
    });
  }
});

module.exports = router;