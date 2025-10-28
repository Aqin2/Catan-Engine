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

  const sendAction = (type: string, kwargs: any = {}) => {
    if (socket?.readyState == WebSocket.OPEN) {
      socket.send(JSON.stringify({
        'action_type': type,
        'kwargs': kwargs
      }));
    }
  }

  const onTileClick = (tile_idx: number) => {
    switch(selected) {
      case 'robber':
        sendAction('move_robber', {'tile_idx': tile_idx});
      break;
    } 
  }

  const onEdgeClick = (edge_idx: number) => {
    switch(selected) {
      case 'road':
        sendAction('road', {'edge_idx': edge_idx});
      break;
    }    
  }
  

  const onNodeClick = (node_idx: number) => {
    switch(selected) {
      case 'settlement':
        sendAction('settlement', {'node_idx': node_idx});
      break;
      case 'city':
        sendAction('city', {'node_idx': node_idx});
      break;
    }
  }


  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => setSocket(ws);
    ws.onclose = () => setSocket(null);


    ws.onmessage = (event) => {
      let game: game = JSON.parse(event.data);
      
      setGame(game);
      console.log(game);
      game.info.forEach((x) => console.log(x));
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
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('end_turn')}>End Turn</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('roll')}>Roll Dice</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('buy_dev')}>Buy Dev Card</Button>
      </div>
      <div>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('play_dev', {'dev_type': 'knight'})}>Knight</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('play_dev', {'dev_type': 'monopoly'})}>Monopoly</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('play_dev', {'dev_type': 'road_build'})}>Road Building</Button>
        <Button variant='outline-light' className='me-2 game-button' onClick={() => sendAction('play_dev', {'dev_type': 'invention'})}>Invention</Button>
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
