/**
 * Utility functions for parsing and extracting JSON from various text formats
 */

/**
 * Extract JSON from text that may contain markdown, extra text, or formatting
 * @param {string} text - Raw text containing JSON
 * @returns {Object} Parsed JSON object
 */
function extractJSON(text) {
  try {
    // First, try to parse the text directly as JSON
    return JSON.parse(text);
  } catch (error) {
    // If direct parsing fails, try to extract JSON from the text
    return extractJSONFromText(text);
  }
}

/**
 * Extract JSON from text using various strategies
 * @param {string} text - Text containing JSON
 * @returns {Object} Extracted JSON object
 */
function extractJSONFromText(text) {
  // Strategy 1: Look for JSON between code blocks (```json ... ```)
  let jsonMatch = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/i);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[1]);
    } catch (error) {
      // Continue to next strategy
    }
  }

  // Strategy 2: Look for JSON between curly braces
  jsonMatch = text.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[0]);
    } catch (error) {
      // Continue to next strategy
    }
  }

  // Strategy 3: Clean the text and try parsing
  const cleanedText = cleanTextForJSON(text);
  try {
    return JSON.parse(cleanedText);
  } catch (error) {
    // Strategy 4: Try to fix common JSON issues
    const fixedText = fixCommonJSONIssues(cleanedText);
    try {
      return JSON.parse(fixedText);
    } catch (finalError) {
      throw new Error(`Failed to extract valid JSON from text: ${finalError.message}`);
    }
  }
}

/**
 * Clean text to prepare for JSON parsing
 * @param {string} text - Raw text
 * @returns {string} Cleaned text
 */
function cleanTextForJSON(text) {
  return text
    .replace(/```json/gi, '') // Remove markdown JSON indicators
    .replace(/```/g, '') // Remove markdown code blocks
    .replace(/^\s*[\w\s]*?(?=\{)/i, '') // Remove text before first {
    .replace(/\}[\s\S]*$/, '}') // Remove text after last }
    .trim();
}

/**
 * Fix common JSON formatting issues
 * @param {string} text - JSON text with potential issues
 * @returns {string} Fixed JSON text
 */
function fixCommonJSONIssues(text) {
  return text
    .replace(/,(\s*[}\]])/g, '$1') // Remove trailing commas
    .replace(/([{,]\s*)(\w+):/g, '$1"$2":') // Add quotes to unquoted keys
    .replace(/:\s*([^",{\[\]}\s][^",{\[\]}\n]*?)(\s*[,}\]])/g, ':"$1"$2') // Add quotes to unquoted string values
    .replace(/:\s*'([^']*)'/g, ':"$1"') // Replace single quotes with double quotes
    .replace(/\n/g, ' ') // Replace newlines with spaces
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();
}

/**
 * Validate if a string contains valid JSON
 * @param {string} text - Text to validate
 * @returns {boolean} True if valid JSON
 */
function isValidJSON(text) {
  try {
    JSON.parse(text);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Safely parse JSON with fallback to empty object
 * @param {string} text - JSON text
 * @param {Object} fallback - Fallback object if parsing fails
 * @returns {Object} Parsed object or fallback
 */
function safeJSONParse(text, fallback = {}) {
  try {
    return extractJSON(text);
  } catch (error) {
    console.warn('JSON parsing failed, using fallback:', error.message);
    return fallback;
  }
}

/**
 * Format JSON for better readability
 * @param {Object} obj - Object to format
 * @param {number} indent - Indentation spaces
 * @returns {string} Formatted JSON string
 */
function formatJSON(obj, indent = 2) {
  try {
    return JSON.stringify(obj, null, indent);
  } catch (error) {
    throw new Error(`Failed to format JSON: ${error.message}`);
  }
}

module.exports = {
  extractJSON,
  extractJSONFromText,
  cleanTextForJSON,
  fixCommonJSONIssues,
  isValidJSON,
  safeJSONParse,
  formatJSON
};