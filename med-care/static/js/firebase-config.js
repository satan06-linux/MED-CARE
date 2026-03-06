// Firebase Web SDK Configuration
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDtawLZb3XTIhc3oaDNK4Kg0K5D2vioAUM",
  authDomain: "med-care-f2d63.firebaseapp.com",
  projectId: "med-care-f2d63",
  storageBucket: "med-care-f2d63.firebasestorage.app",
  messagingSenderId: "360190835550",
  appId: "1:360190835550:web:436f8e99f6a929f7a92dcf",
  measurementId: "G-NJGEL2Q2GW"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };