import type React from "react";
import { Button } from "react-bootstrap";

interface GameButtonProps {
    name: string,
    selected: boolean,
    setSelected: React.Dispatch<React.SetStateAction<string | null>>
}

const GameButton: React.FC<GameButtonProps> = ({
    name,
    selected,
    setSelected
}) => {


    return <Button
        variant='outline-light'
        className={'me-2 game-button' + (selected ? ' selected' : '')}
        onClick={() => setSelected(name)}>
            {name}
    </Button>
}

export default GameButton