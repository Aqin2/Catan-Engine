import type React from "react";
import BoardEdge from "./BoardEdge";
import BoardNode from "./BoardNode";
import coords from "./coords.json";

import type { game } from './types';
import BoardTile from "./BoardTile";

interface BoardProps {
  width: number
};

const player_colors = [
  'blue',
  'red',
  'lightgray', //white
  'orange'
]
const tile_coords = coords.tile_coords;
const edge_endpoints = coords.edge_endpoints;
const node_coords = coords.node_coords;

const SIN_60 = Math.sin(Math.PI / 3);

const xy_coords = (qrs_coords: number[], scale: number) => {
  return [
    qrs_coords[0] * scale + qrs_coords[1] * scale * 0.5,
    qrs_coords[1] * scale * SIN_60
  ]
}

interface BoardProps {
  game?: game,
  width: number,
  onTileClick: (coords: number[]) => void,
  onEdgeClick: (coords: number[]) => void,
  onNodeClick: (coords: number[]) => void
};

const Board: React.FC<BoardProps> = ({
  game,
  width,
  onTileClick,
  onEdgeClick,
  onNodeClick
}) => {
  const scale = width / 30;

  if (!game)
    return <></>;

  return <svg
    viewBox={`${-scale * 15} ${-scale * 12 / SIN_60} ${scale * 30} ${scale * 24 / SIN_60}`}
    width={scale * 30}
    height={scale * 24 / SIN_60}
    style={{
      'overflow': 'visible',
      'padding': '10px'
    }}>
    {tile_coords.map((coords, i) => {
      const width = scale * 6;
      const [x, y] = xy_coords(coords, scale);

      return <BoardTile
        key={`tile_${i}`}
        x={x}
        y={y}
        width={width}
        tile={game.board.tiles[i]}
        has_robber={game.board.robber_tile == i}
        onTileClick={() => onTileClick(coords)}
      />
    })}
    {edge_endpoints.map((endpoints, i) => {
      const [x1, y1] = xy_coords(endpoints[0], scale);
      const [x2, y2] = xy_coords(endpoints[1], scale);
      const coords = endpoints[0].map((x, i) => (x + endpoints[1][i]) / 2)

      let color = 'black'
      if (game.board.edges[i]) {
        color = player_colors[game.players.indexOf(game.board.edges[i])]
      }

      return <BoardEdge
        key={`edge_${i}`}
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth={10}
        onClick={() => {onEdgeClick(coords)}}
      />
    })}
    {node_coords.map((coords, i) => {
      const [cx, cy] = xy_coords(coords, scale);
      let color = 'black'
      if (game.board.nodes[i].player) {
        color = player_colors[game.players.indexOf(game.board.nodes[i].player)]
      }

      return <BoardNode
        key={`node_${i}`}
        rad={10}
        cx={cx}
        cy={cy}
        fill={color}
        onClick={() => {onNodeClick(coords)}}
      />
    })}
  </svg>
};

export default Board;