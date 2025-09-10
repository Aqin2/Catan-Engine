import type React from "react";
import type { tile } from "./types";

import brick from './assets/tile_brick.svg';
import wood from './assets/tile_wood.svg';
import wool from './assets/tile_sheep.svg';
import wheat from './assets/tile_wheat.svg';
import ore from './assets/tile_ore.svg';
import desert from './assets/tile_desert.svg';
import robber from './assets/robber.png';

const tile_images = {
  'brick': brick,
  'wood': wood,
  'wool': wool,
  'wheat': wheat,
  'ore': ore,
  'desert': desert
}

interface BoardTileProps {
  x: number,
  y: number,
  width: number,
  tile: tile,
  has_robber?: boolean,
  onTileClick: () => void
}

const SIN_60 = Math.sin(Math.PI / 3);

const BoardTile: React.FC<BoardTileProps> = ({
  x,
  y,
  width,
  tile,
  has_robber=false,
  onTileClick
}) => {
  const resource = tile.resource
  const num = tile.number
  const height = width / SIN_60

  const robber_width = width / 4
  const robber_height = robber_width * 2

  return <g onClick={onTileClick}>
    <image
      key={'tile_img'}
      className='game-tile'
      href={tile_images[resource]}
      x={x - width / 2}
      y={y - height / 2}
      width={width}
      height={height}
    />
    {num > 0 ? <>
      <circle
        key={'circle'}
        cx={x}
        cy={y}
        r={width / 6}
        fill='white'
      />
      <text
        key={'text'}
        textAnchor='middle'
        dominantBaseline='central'
        className={'game-number-text' + (num == 6 || num == 8 ? ' red' : '')}
        x={x}
        y={y}
      >
        {num}
      </text>
    </>
      : <></>}
    {has_robber ? <>
      <image
        key={'robber_img'}
        href={robber}
        x={x + robber_width / 2}
        y={y - robber_height / 2}
        width={robber_width}
        height={robber_height}
      />
    </> : <></>}
  </g>
}

export default BoardTile;