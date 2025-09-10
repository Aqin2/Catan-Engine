import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import Board from './Board'
import GameButton from './GameButton'
import { useState, useEffect } from 'react'
import type { game } from './types' 
import { Button } from 'react-bootstrap'




function App() {
  const [selected, setSelected] = useState<string | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [game, setGame] = useState<game | null>(null);

  const onEdgeClick = (coords: number[]) => {
    if (selected == 'Road') {
      if (socket?.readyState == WebSocket.OPEN) {
        socket.send(JSON.stringify({
          'action_type': 'road',
          'kwargs': {
            'coords': coords
          }
        }));
      }
    }
  }

  const onNodeClick = (coords: number[]) => {
    if (selected == 'Settlement' || selected == 'City') {
      if (socket?.readyState == WebSocket.OPEN) {
        socket.send(JSON.stringify({
          'action_type': 'structure',
          'kwargs': {
            'coords': coords,
            'value': selected == 'Settlement' ? 1 : 2
          }
        }));
      }
    }
  }


  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => setSocket(ws);
    ws.onclose = () => setSocket(null);


    ws.onmessage = (event) => {
      console.log(JSON.parse(event.data));
      setGame(JSON.parse(event.data));
    };

    return () => {
      if (ws.readyState == WebSocket.OPEN)
        ws.close();
    };
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Board
        game={game ? game : undefined}
        width={600}
        onTileClick={(coords) => console.log('clicked tile ' + coords)}
        onEdgeClick={(coords) => onEdgeClick(coords)} 
        onNodeClick={(coords) => onNodeClick(coords)}
      />
      <div>
        <GameButton name={'Road'} selected={selected == 'Road'} setSelected={setSelected}/>
        <GameButton name={'Settlement'} selected={selected == 'Settlement'} setSelected={setSelected}/>
        <GameButton name={'City'} selected={selected == 'City'} setSelected={setSelected}/>
      </div>
      <div>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => {
          if (socket?.readyState == WebSocket.OPEN)
            socket.send(JSON.stringify({
              'action_type': 'end_turn',
              'kwargs': {}
            }));
        }}>End Turn</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => {
          if (socket?.readyState == WebSocket.OPEN)
            socket.send(JSON.stringify({
              'action_type': 'roll',
              'kwargs': {}
            }));
        }}>Roll Dice</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => {
          if (socket?.readyState == WebSocket.OPEN)
            socket.send(JSON.stringify({
              'action_type': 'buy_dev',
              'kwargs': {}
            }));
        }}>Buy Dev Card</Button>
      </div>
    </div>
  )
}

export default App;
