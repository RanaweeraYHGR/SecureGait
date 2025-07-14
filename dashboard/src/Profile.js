import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { collection, query, where, getDocs, orderBy } from 'firebase/firestore';
import { db } from './firebase';

const Profile = () => {
  const { name } = useParams();
  const [profile, setProfile] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfileAndHistory = async () => {
      try {
        // Fetch profile
        const profileQuery = query(collection(db, 'userprofile'), where('name', '==', name));
        const profileSnapshot = await getDocs(profileQuery);
        
        if (!profileSnapshot.empty) {
          const userProfile = profileSnapshot.docs[0].data();
          setProfile(userProfile);

          // Fetch history
          const nameQuery = query(
            collection(db, 'detections'),
            where('name', '==', userProfile.name),
            orderBy('timestamp', 'desc')
          );
          const nameSnapshot = await getDocs(nameQuery);
          let historyData = nameSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

          if (userProfile.nickname) {
            const nicknameQuery = query(
              collection(db, 'detections'),
              where('name', '==', userProfile.nickname),
              orderBy('timestamp', 'desc')
            );
            const nicknameSnapshot = await getDocs(nicknameQuery);
            const nicknameData = nicknameSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
            historyData = [...historyData, ...nicknameData];
          }

          // Sort the combined history
          historyData.sort((a, b) => b.timestamp.seconds - a.timestamp.seconds);

          setHistory(historyData);

        } else {
          setProfile(null); // No user found
        }
      } catch (error) {
        console.error("Error fetching data: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfileAndHistory();
  }, [name]);

  if (loading) {
    return <div style={{ padding: '20px', color: '#e0e0e0' }}>Loading...</div>;
  }

  if (!profile) {
    return <div style={{ padding: '20px', color: '#e0e0e0' }}>User not found.</div>;
  }

  return (
    <div>
      <div className="premium-card" style={{ textAlign: 'center' }}>
        <img src={profile.imageUrl} alt={profile.name} style={{ borderRadius: '50%', width: '150px', height: '150px', objectFit: 'cover', border: '4px solid #90ee90' }} />
        <h1>{profile.name}</h1>
        <p><strong>Age:</strong> {profile.age}</p>
        <p><strong>Position:</strong> {profile.position}</p>
        {profile.nickname && <p><strong>Nickname:</strong> {profile.nickname}</p>}
      </div>

      <div className="premium-card" style={{ marginTop: '20px' }}>
        <h2>Detection History</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr>
              <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <tr key={item.id}>
                <td style={{ padding: '12px', borderBottom: '1px solid #90ee90' }}>{item.name}</td>
                <td style={{ padding: '12px', borderBottom: '1px solid #90ee90' }}>
                  {new Date(item.timestamp.seconds * 1000).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default Profile;