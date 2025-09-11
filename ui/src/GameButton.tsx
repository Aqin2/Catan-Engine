import type React from "react";
import { Button } from "react-bootstrap";

interface GameButtonProps {
    name: string,
    id: string,
    selected: string | null,
    setSelected: React.Dispatch<React.SetStateAction<string | null>>
}

const GameButton: React.FC<GameButtonProps> = ({
    name,
    id,
    selected,
    setSelected
}) => {


    return <Button
        variant='outline-light'
        className={'me-2 game-button' + (selected == id ? ' selected' : '')}
        onClick={() => setSelected(id)}>
            {name}
    </Button>
}

export default GameButton