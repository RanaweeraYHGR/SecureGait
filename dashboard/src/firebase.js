import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Paste YOUR Firebase config here
const firebaseConfig = {
  apiKey: "AIzaSyCgK6atiCfkPkr5sEaW_edgVrGrjsUpM8w",
  authDomain: "person-detector-b687a.firebaseapp.com",
  projectId: "person-detector-b687a",
  storageBucket: "person-detector-b687a.firebasestorage.app",
  messagingSenderId: "973182253205",
  appId: "1:973182253205:web:b6fdadaa6206bbda86039c",
  measurementId: "G-4J9VHZ777S"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(app);
const storage = getStorage(app);

export { db, storage };
