import type React from "react";

interface EdgeProps {
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  stroke: string,
  strokeWidth: number
};

const Edge: React.FC<EdgeProps> = ({
  x1,
  y1,
  x2,
  y2,
  stroke,
  strokeWidth
}) => {
  return <g style={{
    'position': "absolute",
    'strokeLinecap': "round",
  }}>
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={stroke}
      strokeWidth={strokeWidth}
    />
  </g>
}

export default Edge;