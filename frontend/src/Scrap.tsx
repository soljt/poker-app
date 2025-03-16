import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const hello = function() {
  return "Hello World"
}

function App() {
  const [count, setCount] = useState(0)
  const cars = ['Ford', 'BMW', 'Audi']

  const handleClick = () => {
    setCount(count => count + 1)
  }

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <ul>{cars.map((car) => <li>brand is {car}</li>)}</ul>
      <div className="card">
        <button onClick={handleClick}>
          count is {count}
        </button>
        <button onClick={() => alert("BANG")}>Take the shot!</button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR - LOL
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <p>{hello()}</p>
    </>
  )
}

export default App
