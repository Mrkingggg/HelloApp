import React, { useState } from 'react';
import axios from 'axios';

const AddUser = () => {
  const [userData, setUserData] = useState({
    username: '',
    email: '',
    dob: '',
    fullname: '',
    password: '',
    gender: '',
    role_ids: []
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setUserData(prevState => ({
      ...prevState,
      [name]: value
    }));
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/users/add', userData);
      console.log(response.data);
      alert('User added successfully');
    } catch (error) {
      console.error('Error adding user:', error.response.data);
      alert('Failed to add user');
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="username"
        placeholder="Username"
        value={userData.username}
        onChange={handleChange}
      />
      {/* Repeat for other fields */}
      <button type="submit">Add User</button>
    </form>
  );
}

export default AddUser;
