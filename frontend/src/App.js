import React, { useState, useEffect } from 'react';
import './App.css';

// const cors = require('cors')
// const express = require('express')
// const app = express()

// app.use(cors());
function App() {
  // 定义状态：数据（message）、加载状态（isLoading）和错误状态（error）
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 数据请求开始时，设置加载状态为true，错误状态清空
    setIsLoading(true);
    setError(null);

    fetch('http://127.0.0.1:5000/api/users/hello')
      .then(response => {
        if (!response.ok) {
          // 如果响应状态不是2xx，抛出错误
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // 数据加载成功，设置消息状态，加载状态为false
        setMessage(data.message);
        setIsLoading(false);
      })
      .catch(error => {
        // 捕获到错误时，设置错误状态，加载状态为false
        console.error('Error fetching data:', error);
        setError(error.toString());
        setIsLoading(false);
      });
  }, []);

  // 根据不同状态渲染不同UI
  if (isLoading) {
    return <div>Loading...</div>;
  } else if (error) {
    // 当有错误发生时，显示错误信息
    return <div>Error: {error}</div>;
  } else {
    // 数据加载成功且无错误时，显示消息
    return <div>{message}</div>;
  }
}

export default App;

