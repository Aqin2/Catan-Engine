import React from "react";

// Import SVG assets for settlements and cities
import whiteSettlement from './assets/white-settlement.svg';
import whiteCity from './assets/white-city.svg';
import redSettlement from './assets/red-settlement.svg';
import redCity from './assets/red-city.svg';
import blueSettlement from './assets/blue-settlement.svg';
import blueCity from './assets/blue-city.svg';
import orangeSettlement from './assets/orange-settlement.svg';
import orangeCity from './assets/orange-city.svg';

// Map color names to settlement/city SVGs
const structureImages = {
  'white': { settlement: whiteSettlement, city: whiteCity },
  'red': { settlement: redSettlement, city: redCity },
  '#b22222': { settlement: redSettlement, city: redCity }, // darker red roads should use red buildings
  'blue': { settlement: blueSettlement, city: blueCity },
  'orange': { settlement: orangeSettlement, city: orangeCity },
  'lightgray': { settlement: whiteSettlement, city: whiteCity }, // Use white for lightgray
  'black': { settlement: whiteSettlement, city: whiteCity } // Use white for black
};

interface BoardNodeProps {
  rad: number,
  hitRad?: number,
  cx: number,
  cy: number,
  fill: string,
  structureType?: 'settlement' | 'city' | null,
  selectedTool?: string | null,
  isAvailableForBuilding?: boolean,
  isUpgradableToCity?: boolean,
  onClick?: () => void
}

const BoardNode: React.FC<BoardNodeProps> = ({
  rad,
  hitRad = rad * 2,
  cx,
  cy,
  fill,
  structureType = null,
  selectedTool = null,
  isAvailableForBuilding = false,
  isUpgradableToCity = false,
  onClick = () => { return; }
}) => {
  // If no structure, show empty node (invisible but clickable)
  if (!structureType) {
    return <g>
      {/* Show availability indicator when settlement tool is selected */}
      {isAvailableForBuilding && selectedTool === 'settlement' && (
        <circle
          r={rad * 1.2}
          cx={cx}
          cy={cy}
          fill='rgba(255, 255, 0, 0.3)' // Semi-transparent yellow
          stroke='rgba(255, 255, 0, 0.8)' // Yellow border
          strokeWidth='2'
        />
      )}
      <circle
        r={hitRad}
        cx={cx}
        cy={cy}
        fill='transparent'
        onClick={() => onClick()}
      />
    </g>
  }

  // Get the appropriate SVG based on color and structure type
  const images = structureImages[fill as keyof typeof structureImages] || structureImages['white'];
  const structureImage = structureType === 'city' ? images.city : images.settlement;

  // Size multipliers for settlements vs cities (cities are larger)
  const sizeMultiplier = structureType === 'city' ? 2.0 : 1.5;
  const imageSize = rad * 2 * sizeMultiplier;

  return <g>
    <image
      href={structureImage}
      x={cx - imageSize / 2}
      y={cy - imageSize / 2}
      width={imageSize}
      height={imageSize}
    />
    {/* Show upgrade indicator when city tool is selected and settlement can be upgraded */}
    {isUpgradableToCity && selectedTool === 'city' && (
      <circle
        r={rad * 1.5}
        cx={cx}
        cy={cy}
        fill='rgba(0, 255, 0, 0.4)' // Semi-transparent green
        stroke='rgba(0, 255, 0, 0.9)' // Green border
        strokeWidth='3'
      />
    )}
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