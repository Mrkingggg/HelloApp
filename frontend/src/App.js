import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import AddUser from './AddUser'; // 导入 AddUser 组件
// import HomePage from './HomePage'; // 假设你有一个 HomePage 组件
// import AboutPage from './AboutPage'; // 假设你有一个 AboutPage 组件
// 导入其他需要的组件...

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/api/users/add">Add User</Link>
            </li>
          </ul>
        </nav>

        {/* 路由切换 */}
        <Routes>
          <Route path="/api/users/add" element={<AddUser />} />
          {/* 更多路由... */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
