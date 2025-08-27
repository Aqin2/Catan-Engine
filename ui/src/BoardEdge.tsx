import type React from "react";

interface BoardEdgeProps {
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  stroke: string,
  strokeWidth: number,
  hitWidth?: number
};

const BoardEdge: React.FC<BoardEdgeProps> = ({
  x1,
  y1,
  x2,
  y2,
  stroke,
  strokeWidth,
  hitWidth = strokeWidth * 2
}) => {

  return <g style={{
    'strokeLinecap': 'round'
  }}>
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={stroke}
      strokeWidth={strokeWidth}
    />
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke='transparent'
      strokeWidth={hitWidth}
      onClick={() => console.log('edge clicked')}
    />
  </g>
}

export default BoardEdge;