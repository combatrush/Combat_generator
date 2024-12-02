import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AnimationWorkspace } from './components/Animation/AnimationWorkspace';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<AnimationWorkspace />} />
      </Routes>
    </div>
  );
}

export default App;
