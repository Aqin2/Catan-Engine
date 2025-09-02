import React from "react";

interface BoardNodeProps {
  rad: number,
  hitRad?: number,
  cx: number,
  cy: number,
  fill: string,
  onClick?: () => void
}

const BoardNode: React.FC<BoardNodeProps> = ({
  rad,
  hitRad = rad * 2,
  cx,
  cy,
  fill,
  onClick = () => { return; }
}) => {
  return <g>
    <circle
      r={rad}
      cx={cx}
      cy={cy}
      fill={fill}
    />
    <circle
      r={hitRad}
      cx={cx}
      cy={cy}
      fill='transparent'
      onClick={() => onClick()}
    />
  </g>
}

export default BoardNode;