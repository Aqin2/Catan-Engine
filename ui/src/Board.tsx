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

// Check if a settlement can be placed at the given coordinates
// Settlements must be at least 2 edges away from any other settlement/city
const isValidSettlementLocation = (targetCoords: number[], nodes: any[], node_coords: number[][]) => {
  for (let i = 0; i < nodes.length; i++) {
    // Skip if this node is empty
    if (!nodes[i].player) continue;

    // Get the coordinates of the existing settlement/city
    const existingCoords = node_coords[i];

    // Calculate distance using cubic coordinate distance formula
    // distance = max(|q1-q2|, |r1-r2|, |s1-s2|)
    const dq = Math.abs(targetCoords[0] - existingCoords[0]);
    const dr = Math.abs(targetCoords[1] - existingCoords[1]);
    const ds = Math.abs(targetCoords[2] - existingCoords[2]);

    const distance = Math.max(dq, dr, ds);

    // Debug logging
    console.log(`Checking distance between [${targetCoords}] and [${existingCoords}]: distance = ${distance}`);

    // In this coordinate system, adjacent vertices have distance 4
    // Settlements must be at least distance 8 apart (2 edges away)
    if (distance <= 4) {
      console.log(`Too close! Distance ${distance} <= 4 (adjacent vertices)`);
      return false;
    }
  }
  console.log(`Valid location for [${targetCoords}]`);
  return true;
}

// Check if a road can be placed on the given edge
const isValidRoadLocation = (edgeIndex: number, edges: any[], nodes: any[], curPlayer: string, edge_endpoints: number[][][], node_coords: number[][]) => {
  // If edge already has a road, it's not available
  if (edges[edgeIndex]) {
    return false;
  }

  // Get the two endpoints of this edge
  const edgeCoords = edge_endpoints[edgeIndex];
  const node1Coords = edgeCoords[0];
  const node2Coords = edgeCoords[1];

  // Find the node indices for these coordinates
  let node1Index = -1;
  let node2Index = -1;

  for (let i = 0; i < node_coords.length; i++) {
    const currentNodeCoords = node_coords[i];
    if (currentNodeCoords && currentNodeCoords.length >= 3) {
      if (currentNodeCoords[0] === node1Coords[0] &&
          currentNodeCoords[1] === node1Coords[1] &&
          currentNodeCoords[2] === node1Coords[2]) {
        node1Index = i;
      }
      if (currentNodeCoords[0] === node2Coords[0] &&
          currentNodeCoords[1] === node2Coords[1] &&
          currentNodeCoords[2] === node2Coords[2]) {
        node2Index = i;
      }
    }
  }

  // Check if either endpoint has the player's settlement/city
  if ((node1Index >= 0 && nodes[node1Index].player === curPlayer) ||
      (node2Index >= 0 && nodes[node2Index].player === curPlayer)) {
    return true;
  }

  // Check if either endpoint is connected to the player's road
  // For each endpoint, check if any adjacent edge has the player's road
  for (let nodeIndex of [node1Index, node2Index]) {
    if (nodeIndex >= 0 && !nodes[nodeIndex].player) {
      // Empty node - check for adjacent edges that might have player's road
      // Since we don't have full adjacency data, we'll use a coordinate-based approximation
      const nodeCoord = node_coords[nodeIndex];

      // Check all edges to see if any are close to this node and owned by player
      for (let j = 0; j < edges.length; j++) {
        if (edges[j] === curPlayer) {
          // This edge belongs to the player, check if it's adjacent to our node
          const playerEdgeCoords = edge_endpoints[j];
          const edgeNode1 = playerEdgeCoords[0];
          const edgeNode2 = playerEdgeCoords[1];

          // Check if this player edge shares a node with our target edge
          if ((edgeNode1[0] === nodeCoord[0] && edgeNode1[1] === nodeCoord[1] && edgeNode1[2] === nodeCoord[2]) ||
              (edgeNode2[0] === nodeCoord[0] && edgeNode2[1] === nodeCoord[1] && edgeNode2[2] === nodeCoord[2])) {
            return true;
          }
        }
      }
    }
  }

  return false;
}

interface BoardProps {
  game?: game,
  width: number,
  selectedTool?: string | null,
  onTileClick: (coords: number[]) => void,
  onEdgeClick: (coords: number[]) => void,
  onNodeClick: (coords: number[]) => void
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
        onTileClick={() => onTileClick(coords)}
      />
    })}
    {edge_endpoints.map((endpoints, i) => {
      const [x1, y1] = xy_coords(endpoints[0], scale);
      const [x2, y2] = xy_coords(endpoints[1], scale);
      const coords = endpoints[0].map((x, i) => (x + endpoints[1][i]) / 2)

      let color = 'black'
      let isAvailableForRoad = false;

      if (game.board.edges[i]) {
        color = player_colors[game.player_names.indexOf(game.board.edges[i])]
      } else if (selectedTool === 'road') {
        // Check if road can be placed here
        isAvailableForRoad = isValidRoadLocation(i, game.board.edges, game.board.nodes, game.cur_player, edge_endpoints, node_coords);
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
        onClick={() => {onEdgeClick(coords)}}
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
          isAvailableForBuilding = isValidSettlementLocation(coords, game.board.nodes, node_coords);
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
        onClick={() => {onNodeClick(coords)}}
      />
    })}
  </svg>
};

export default Board;