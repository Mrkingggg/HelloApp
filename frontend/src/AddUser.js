// AddUser.js
import React, { useState } from 'react';
import axios from 'axios';

const AddUser = () => {
  // 初始化表单状态
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    dob: '',
    fullname: '',
    password: '',
    gender: '',
    role_ids: []
  });

  // 处理表单输入变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // 处理表单提交
  const handleSubmit = async (e) => {
    e.preventDefault(); // 阻止表单默认提交行为

    // 发送 POST 请求到后端
    try {
      const response = await axios.post('http://localhost:5050/api/users/add', formData);
      alert('User added successfully');
      console.log(response.data);
    } catch (error) {
      console.error('Failed to add user:', error);
      alert('Failed to add user');
    }
  };

  return (
    <div>
      <h2>Add User</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" name="username" value={formData.username} onChange={handleChange} placeholder="Username" required />
        <input type="text" name="password" value={formData.password} onChange={handleChange} placeholder="password" required />
        <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Email" required />
        <p>dob:</p>
        <input type="date" name="dob" value={formData.dob} onChange={handleChange} placeholder="Dob" required />
        <input type="text" name="fullname" value={formData.fullname} onChange={handleChange} placeholder="fullname" required />
        <select name="gender" value={formData.gender} onChange={handleChange} required>
          <option value="">Select Gender</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
          <option value="other">Other</option>
        </select>
  // remain to design role id input

        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default AddUser;
