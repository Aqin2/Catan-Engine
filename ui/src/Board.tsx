import type React from "react";
import BoardEdge from "./BoardEdge";
import BoardNode from "./BoardNode";
import coords from "./coords.json";

import type { game } from './types';
import BoardTile from "./BoardTile";

const player_colors = [
  'blue',
  '#b22222', // darker red
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
  selectedTool?: string | null,
  onTileClick: (tile_idx: number) => void,
  onEdgeClick: (edge_idx: number) => void,
  onNodeClick: (node_idx: number) => void
};

const Board: React.FC<BoardProps> = ({
  game,
  width,
  selectedTool,
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
        onTileClick={() => onTileClick(i)}
      />
    })}
    {edge_endpoints.map((endpoints, i) => {
      const [x1, y1] = xy_coords(endpoints[0], scale);
      const [x2, y2] = xy_coords(endpoints[1], scale);

      let color = 'black'
      let isAvailableForRoad = false;

      if (game.board.edges[i]) {
        color = player_colors[game.player_names.indexOf(game.board.edges[i])]
      } else if (selectedTool === 'road') {
        // Check if road can be placed here
        isAvailableForRoad = game.players[game.cur_player].available_roads[i]
      }

      return <BoardEdge
        key={`edge_${i}`}
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth={10}
        selectedTool={selectedTool}
        isAvailableForRoad={isAvailableForRoad}
        onClick={() => {onEdgeClick(i)}}
      />
    })}
    {node_coords.map((coords, i) => {
      const [cx, cy] = xy_coords(coords, scale);
      let color = 'black'
      let structureType: 'settlement' | 'city' | null = null;
      let isAvailableForBuilding = false;

      if (game.board.nodes[i].player) {
        color = player_colors[game.player_names.indexOf(game.board.nodes[i].player)]
        // Determine structure type based on node value (1 = settlement, 2 = city)
        if (game.board.nodes[i].value === 1) {
          structureType = 'settlement';
        } else if (game.board.nodes[i].value === 2) {
          structureType = 'city';
        }
      } else {
        // Empty node - check if available for building when settlement tool is selected
        if (selectedTool === 'settlement') {
          // Check distance rule: settlements must be at least 2 edges away from any other settlement/city
          isAvailableForBuilding = game.players[game.cur_player].available_settlements[i]
        }
        // Note: No yellow indicators for cities - they will be validated by backend
      }

      // Check if this is a settlement owned by current player that can be upgraded to city
      let isUpgradableToCity = false;
      if (game.board.nodes[i].player &&
          game.board.nodes[i].value === 1 && // It's a settlement (not city)
          game.board.nodes[i].player === game.cur_player && // Owned by current player
          selectedTool === 'city') { // City tool is selected
        isUpgradableToCity = true;
      }

      return <BoardNode
        key={`node_${i}`}
        rad={10}
        cx={cx}
        cy={cy}
        fill={color}
        structureType={structureType}
        selectedTool={selectedTool}
        isAvailableForBuilding={isAvailableForBuilding}
        isUpgradableToCity={isUpgradableToCity}
        onClick={() => {onNodeClick(i)}}
      />
    })}
  </svg>
};

export default Board;