import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { db, storage } from './firebase';
import { uploadImage } from './supabaseImageUpload';

const UpdateUser = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [position, setPosition] = useState('');
  const [nickname, setNickname] = useState('');
  const [image, setImage] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const userDoc = doc(db, 'userprofile', userId);
      const userSnapshot = await getDoc(userDoc);
      if (userSnapshot.exists()) {
        const userData = userSnapshot.data();
        setName(userData.name);
        setAge(userData.age);
        setPosition(userData.position);
        setNickname(userData.nickname || '');
        setImageUrl(userData.imageUrl);
      } else {
        alert('User not found.');
        navigate('/admin');
      }
      setLoading(false);
    };
    fetchUser();
  }, [userId, navigate]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (allowedTypes.includes(file.type)) {
        setImage(file);
      } else {
        alert('Only .jpg, .jpeg, and .png file types are allowed.');
        e.target.value = null;
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      let newImageUrl = imageUrl;
      if (image) {
        const uploadResult = await uploadImage(image, 'user-profiles');
        if (!uploadResult.success) {
          throw new Error(uploadResult.error);
        }
        newImageUrl = uploadResult.publicUrl;
      }

      const userDoc = doc(db, 'userprofile', userId);
      await updateDoc(userDoc, {
        name,
        age,
        position,
        nickname,
        imageUrl: newImageUrl,
      });

      alert('User data updated successfully!');
      navigate('/admin');
    } catch (error) {
      console.error('Error updating data: ', error);
      alert('Failed to update user data.');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="premium-card">
      <h1>Update User</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '10px' }}>
          <label>Name:</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} required style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#333', border: '1px solid #444', color: '#e0e0e0' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Age:</label>
          <input type="number" value={age} onChange={(e) => setAge(e.target.value)} required style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#333', border: '1px solid #444', color: '#e0e0e0' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Position:</label>
          <input type="text" value={position} onChange={(e) => setPosition(e.target.value)} required style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#333', border: '1px solid #444', color: '#e0e0e0' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Nickname (Optional):</label>
          <input type="text" value={nickname} onChange={(e) => setNickname(e.target.value)} style={{ width: '100%', padding: '8px', boxSizing: 'border-box', backgroundColor: '#333', border: '1px solid #444', color: '#e0e0e0' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Profile Picture:</label>
          <input type="file" onChange={handleImageChange} />
          {imageUrl && !image && <img src={imageUrl} alt="current profile" style={{ width: '100px', height: '100px', marginTop: '10px' }} />}
        </div>
        <button type="submit" disabled={uploading} style={{ padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {uploading ? 'Updating...' : 'Update Data'}
        </button>
      </form>
    </div>
  );
};

export default UpdateUser;