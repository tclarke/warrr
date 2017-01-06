import {Http} from "@angular/http";
import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {Board} from "../core/board.class";
import "rxjs/add/operator/map";
import "rxjs/add/operator/mergeMap";

@Injectable()
export class BoardService {
    private baseUrl = "http://localhost:8000/api/v1/";

    constructor(private http: Http) {
    }

    createBoard(): Observable<Board> {
        return this.http
            .post(this.baseUrl + "/boards/", {})
            .map(res => res.json())
            .map(result => {
                return new Board(result, this);
            });
    }

    saveState(state) {
        return this.http
            .post(this.baseUrl + "/boards/" + state.id, state)
    }
}
