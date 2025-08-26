import type React from "react";
import Edge from "./Edge";
import coords from "./coords.json";

interface BoardProps {
  width: number
};

const tile_coords = coords.tile_coords;
const edge_coords = coords.edge_coords;
const node_coords = coords.node_coords;

const SIN_60 = Math.sin(Math.PI / 3);

const Board: React.FC<BoardProps> = ({
  width
}) => {
  const scale = width / 30;

  return <svg
    viewBox={`${-scale * 15} ${-scale * 12 / SIN_60} ${scale * 30} ${scale * 24 / SIN_60}`}
    width={scale * 30}
    height={scale * 24 / SIN_60}
    style={{
      'position': 'relative',
      'overflow': 'visible',
      'padding': '10px'
    }}>
    {tile_coords.map((coords, i) => {
      return <text
        key={`tile_${i}`}
        x={coords[0] * scale + coords[1] * scale * 0.5}
        y={coords[1] * scale * SIN_60}
        style={{
          'position': 'absolute',
          'textAnchor': 'middle',
          'dominantBaseline': 'central'
        }}>{i}</text>
    })}
    {edge_coords.map((endpoints, i) => {
      return <Edge
        key={`edge_${i}`}
        x1={endpoints[0][0] * scale + endpoints[0][1] * scale * 0.5}
        y1={endpoints[0][1] * scale * Math.sin(Math.PI / 3)}
        x2={endpoints[1][0] * scale + endpoints[1][1] * scale * 0.5}
        y2={endpoints[1][1] * scale * Math.sin(Math.PI / 3)}
        stroke="black"
        strokeWidth={10}
      />
    })}
    {node_coords.map((coords, i) => {
      return <circle
        key={`node_${i}`}
        r={10}
        cx={coords[0] * scale + coords[1] * scale * 0.5}
        cy={coords[1] * scale * SIN_60}
        fill="black"
      />
    })}
  </svg>
};

export default Board;