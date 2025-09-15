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

  const onTileClick = (coords: number[]) => {
    switch(selected) {
      case 'robber':
        if (socket?.readyState == WebSocket.OPEN) {
          socket.send(JSON.stringify({
            'action_type': 'move_robber',
            'kwargs': {
              'coords': coords
            }
          }));
        }
      break;
    } 
  }

  const onEdgeClick = (coords: number[]) => {
    switch(selected) {
      case 'road':
        if (socket?.readyState == WebSocket.OPEN) {
          socket.send(JSON.stringify({
            'action_type': 'road',
            'kwargs': {
              'coords': coords
            }
          }));
        }
      break;
    }    
  }
  

  const onNodeClick = (coords: number[]) => {
    switch(selected) {
      case 'settlement':
      case 'city':
        if (socket?.readyState == WebSocket.OPEN) {
          socket.send(JSON.stringify({
            'action_type': 'structure',
            'kwargs': {
              'coords': coords,
              'value': selected == 'settlement' ? 1 : 2
            }
          }));
        }
      break;
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
        selectedTool={selected}
        onTileClick={(coords) => onTileClick(coords)}
        onEdgeClick={(coords) => onEdgeClick(coords)}
        onNodeClick={(coords) => onNodeClick(coords)}
      />
      <div>
        <GameButton name={'Road'} id={'road'} selected={selected} setSelected={setSelected}/>
        <GameButton name={'Settlement'} id={'settlement'} selected={selected} setSelected={setSelected}/>
        <GameButton name={'City'} id={'city'} selected={selected} setSelected={setSelected}/>
        <GameButton name={'Move Robber'} id={'robber'} selected={selected} setSelected={setSelected}/>
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
      {game ? <div>
        {Object.entries(game.players).map(([name, player], i) => {
          return <div key={`player_${i}`}>
            <h1>{name}</h1>
            <p>
              {JSON.stringify(player.resources)} 
            </p>
            <p>
              {JSON.stringify(player.dev_cards)}
            </p>
          </div>
        })}


      </div> : <></>}
      

    </div>
  )
}

export default App;
