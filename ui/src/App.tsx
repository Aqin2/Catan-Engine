import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import Board from './Board'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Board width={600}></Board>
    </>
  )
}

export default App
