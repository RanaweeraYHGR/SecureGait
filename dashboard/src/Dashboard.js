import React, { useEffect, useState } from "react";
import { collection, query, orderBy, onSnapshot, getDocs } from "firebase/firestore";
import { db } from "./firebase";
import { Link } from "react-router-dom";
import "./App.css";

function Dashboard() {
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    const fetchDetections = async () => {
      // First, get a list of active users and their nicknames
      const usersQuerySnapshot = await getDocs(collection(db, 'userprofile'));
      const activeUsers = new Map();
      usersQuerySnapshot.forEach(doc => {
        const userData = doc.data();
        if (userData.active) {
          const userDisplayData = { name: userData.name, imageUrl: userData.imageUrl };
          activeUsers.set(userData.name.toLowerCase(), userDisplayData);
          if (userData.nickname) {
            activeUsers.set(userData.nickname.toLowerCase(), userDisplayData);
          }
        }
      });

      const q = query(collection(db, "detections"), orderBy("timestamp", "desc"));
      const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const items = [];
        querySnapshot.forEach((doc) => {
          const detection = doc.data();
          const detectionName = detection.name.toLowerCase();
          // Check if the detected name or nickname is in our active list
          if (activeUsers.has(detectionName)) {
            // Use the canonical name from our map for the link
            const userData = activeUsers.get(detectionName);
            items.push({ id: doc.id, ...detection, name: userData.name, imageUrl: userData.imageUrl });
          }
        });
        setDetections(items);
      });

      return () => unsubscribe();
    };

    fetchDetections();
  }, []);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) {
      return "N/A";
    }

    let date;
    // Firestore timestamps can be objects with a toDate method.
    if (timestamp.toDate && typeof timestamp.toDate === 'function') {
      date = timestamp.toDate();
    } else {
      // Or they can be ISO strings.
      date = new Date(timestamp);
    }

    if (isNaN(date.getTime())) {
      return "Invalid Date";
    }

    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="premium-card">
      <h1>Person Detection Dashboard</h1>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px" }}>
        <thead>
          <tr>
            <th style={{ padding: "12px", borderBottom: "1px solid #90ee90", textAlign: "left" }}>Name</th>
            <th style={{ padding: "12px", borderBottom: "1px solid #90ee90", textAlign: "left" }}>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((det, index) => (
            <tr key={det.id} className="fade-in">
              <td style={{ padding: "12px", borderBottom: "1px solid #90ee90", display: 'flex', alignItems: 'center' }}>
                {det.imageUrl && <img src={det.imageUrl} alt={det.name} className="profile-pic" />}
                <Link to={`/profile/${det.name}`} style={{ color: "#61dafb", marginLeft: '10px' }}>
                  {det.name || "Unknown"}
                </Link>
              </td>
              <td style={{ padding: "12px", borderBottom: "1px solid #90ee90" }}>{formatTimestamp(det.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;
