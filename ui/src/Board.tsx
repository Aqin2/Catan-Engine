import type React from "react";
import BoardEdge from "./BoardEdge";
import BoardNode from "./BoardNode";
import coords from "./coords.json";

import brick from './assets/brick.png';
import wood from './assets/wood.png';
import wool from './assets/wool.png';
import wheat from './assets/wheat.png';
import ore from './assets/ore.png';
import desert from './assets/desert.png';

const assets = [
  brick,
  wood,
  wool,
  wheat,
  ore,
  desert
];

interface BoardProps {
  width: number
};

const tile_coords = coords.tile_coords;
const edge_coords = coords.edge_coords;
const node_coords = coords.node_coords;

const SIN_60 = Math.sin(Math.PI / 3);

const xy_coords = (qrs_coords: number[], scale: number) => {
  return [
    qrs_coords[0] * scale + qrs_coords[1] * scale * 0.5,
    qrs_coords[1] * scale * SIN_60
  ]
}

const Board: React.FC<BoardProps> = ({
  width
}) => {
  const scale = width / 30;

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
      const height = scale * 6 / SIN_60;
      const [x, y] = xy_coords(coords, scale);

      return <image
        key={`tile_${i}`}
        className='game-tile'
        href={assets[i % 6]}
        x={x - width / 2}
        y={y - height / 2}
        width={width}
        height={height}
        onClick={() => console.log('clicked tile ' + i)}
      />
    })}
    {edge_coords.map((endpoints, i) => {
      const [x1, y1] = xy_coords(endpoints[0], scale);
      const [x2, y2] = xy_coords(endpoints[1], scale);

      return <BoardEdge
        key={`edge_${i}`}
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke="black"
        strokeWidth={10}
      />
    })}
    {node_coords.map((coords, i) => {
      const [cx, cy] = xy_coords(coords, scale);

      return <BoardNode
        key={`node_${i}`}
        rad={10}
        cx={cx}
        cy={cy}
        fill="black"
      />
    })}
  </svg>
};

export default Board;