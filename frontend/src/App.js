import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import AddUser from './AddUser'; 


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

       
        <Routes>
          <Route path="/api/users/add" element={<AddUser />} />
         
        </Routes>
      </div>
    </Router>
  );
}

export default App;
