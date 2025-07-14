import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { db, storage } from './firebase';
import { uploadImage } from './supabaseImageUpload';
import { collection, addDoc, getDocs, doc, updateDoc, writeBatch, deleteDoc } from 'firebase/firestore';

const Admin = () => {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [position, setPosition] = useState('');
  const [nickname, setNickname] = useState('');
  const [image, setImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsers = async () => {
      const querySnapshot = await getDocs(collection(db, 'userprofile'));
      const usersData = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setUsers(usersData);
    };
    fetchUsers();
  }, []);

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
    if (!image) {
      alert('Please select an image.');
      return;
    }
    setUploading(true);
    try {
      // Add user to Firestore first, without the image URL
      const docRef = await addDoc(collection(db, 'userprofile'), {
        name,
        age,
        position,
        nickname,
        imageUrl: '', // Initially empty
        active: true,
      });

      // Then, upload the image to Supabase using the utility
      const uploadResult = await uploadImage(image, 'user-profiles');

      if (!uploadResult.success) {
        throw new Error(uploadResult.error);
      }

      // Update the user document with the image URL
      await updateDoc(doc(db, 'userprofile', docRef.id), {
        imageUrl: uploadResult.publicUrl,
      });

      setName('');
      setAge('');
      setPosition('');
      setNickname('');
      setImage(null);
      alert('User data uploaded successfully!');
      
      // Refresh users list
      const querySnapshot = await getDocs(collection(db, 'userprofile'));
      const usersData = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setUsers(usersData);
    } catch (error) {
      console.error('Error uploading data: ', error);
      alert('Failed to upload user data.');
    } finally {
      setUploading(false);
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    const userRef = doc(db, 'userprofile', userId);
    await updateDoc(userRef, {
      active: !currentStatus
    });
    setUsers(users.map(user => user.id === userId ? { ...user, active: !currentStatus } : user));
  };

  const handleAllAction = async (status) => {
    const batch = writeBatch(db);
    users.forEach(user => {
      const userRef = doc(db, 'userprofile', user.id);
      batch.update(userRef, { active: status });
    });
    await batch.commit();
    setUsers(users.map(user => ({ ...user, active: status })));
  };

  const filteredUsers = users
    .filter(user =>
      user.name && user.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteDoc(doc(db, 'userprofile', userId));
        setUsers(users.filter(user => user.id !== userId));
        alert('User deleted successfully!');
      } catch (error) {
        console.error('Error deleting user: ', error);
        alert('Failed to delete user.');
      }
    }
  };

  const handleUpdate = (userId) => {
    navigate(`/update-user/${userId}`);
  };

  return (
    <div>
      <h1>Admin Panel</h1>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div className="premium-card" style={{ flex: 1 }}>
          <h2>Add New User</h2>
          <form onSubmit={handleSubmit}>
            {/* Form fields remain the same */}
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
              <input type="file" onChange={handleImageChange} required />
            </div>
            <button type="submit" disabled={uploading} style={{ padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              {uploading ? 'Uploading...' : 'Upload Data'}
            </button>
          </form>
        </div>
        <div className="premium-card" style={{ flex: 2 }}>
          <h2>Manage Users</h2>
          <input
            type="text"
            placeholder="Search by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box', marginBottom: '10px', backgroundColor: '#333', border: '1px solid #444', color: '#e0e0e0' }}
          />
          <div style={{ marginBottom: '10px' }}>
            <button onClick={() => handleAllAction(true)} style={{ marginRight: '10px', padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Activate All</button>
            <button onClick={() => handleAllAction(false)} style={{ padding: '10px 20px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Deactivate All</button>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
            <thead>
              <tr>
                <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Name</th>
                <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Position</th>
                <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Status</th>
                <th style={{ padding: '12px', borderBottom: '1px solid #90ee90', textAlign: 'left' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td style={{ padding: '12px', borderBottom: '1px solid #90ee90' }}>
                    <Link to={`/profile/${user.name}`} style={{ color: '#61dafb' }}>
                      {user.name}
                    </Link>
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #90ee90' }}>{user.position}</td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #90ee90', color: user.active ? '#4CAF50' : '#f44336' }}>{user.active ? 'Active' : 'Inactive'}</td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #90ee90' }}>
                    <button onClick={() => toggleUserStatus(user.id, user.active)} style={{ padding: '5px 10px', backgroundColor: user.active ? '#f44336' : '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      {user.active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button onClick={() => handleUpdate(user.id)} style={{ padding: '5px 10px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginLeft: '5px' }}>
                      Update
                    </button>
                    <button onClick={() => handleDelete(user.id)} style={{ padding: '5px 10px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginLeft: '5px' }}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Admin;