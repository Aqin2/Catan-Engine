import type React from "react";

interface BoardEdgeProps {
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  stroke: string,
  strokeWidth: number,
  hitWidth?: number,
  selectedTool?: string | null,
  isAvailableForRoad?: boolean,
  onClick?: () => void,
};

const BoardEdge: React.FC<BoardEdgeProps> = ({
  x1,
  y1,
  x2,
  y2,
  stroke,
  strokeWidth,
  hitWidth = strokeWidth * 2,
  selectedTool = null,
  isAvailableForRoad = false,
  onClick = () => { return; }
}) => {

  return <g style={{
    'strokeLinecap': 'round'
  }}>
    {/* Show availability indicator when road tool is selected */}
    {isAvailableForRoad && selectedTool === 'road' && (
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke='rgba(255, 255, 0, 0.8)' // Yellow outline on the edge
        strokeWidth={strokeWidth * 1.5}
        strokeLinecap="round"
      />
    )}
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
      onClick={() => onClick()}
    />
  </g>
}

export default BoardEdge;