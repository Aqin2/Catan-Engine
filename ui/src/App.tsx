import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import Board from './Board'
import GameButton from './GameButton'
import { useState } from 'react'

function App() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Board
        width={600}
        onTileClick={(coords) => console.log('clicked tile ' + coords)}
        onEdgeClick={(coords) => {
          if (selected == 'Road') {
            (async () => {
              const response = await fetch('http://127.0.0.1:8000/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  action_type: 'road',
                  kwargs: {
                    coords: coords
                  }
                }
                )})
              const body = await response.json()
              console.log(body)
            })();
          }
        }} 
        onNodeClick={(coords) => console.log('clicked node ' + coords)}
      />
      <div>
        <GameButton name={'Road'} selected={selected == 'Road'} setSelected={setSelected}/>
        <GameButton name={'Settlement'} selected={selected == 'Settlement'} setSelected={setSelected}/>
        <GameButton name={'City'} selected={selected == 'City'} setSelected={setSelected}/>
      </div>
      
    </div>
  )
}

export default App
