import {BoardService} from "../services/board.service";

export class Board {
    public id: string;
    public pieces: any[];

    constructor(public obj, private boardService: BoardService) {
        this.id = obj.id;
    }

    saveState() {
        let state = {
                id: this.id,
            };
        return this.boardService.saveState(state);
    }
}
