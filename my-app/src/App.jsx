import { useState } from 'react'
import './App.css'

function App() {
  const [text, setText] = useState('')

  const handleSubmit = () => {
    console.log('Submitted:', text)
  }

  return (
    <div className="container">
      <h1>Oral ESL</h1>
      <input
        type="text"
        className="text-field"
        placeholder="Type something..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="submit-btn" onClick={handleSubmit}>
        Submit
      </button>
    </div>
  )
}

export default App
