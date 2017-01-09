import {Http} from "@angular/http";
import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import "rxjs/add/operator/map";
import "rxjs/add/operator/mergeMap";

@Injectable()
export class MarkerService {
    private baseUrl = "http://localhost:8000/api/v1/";

    constructor(private http: Http) {
    }

    getMarkerTypes(): Observable<any[]> {
        return this.http
            .get(this.baseUrl + "pieces/?per_page=-1")
            .map(res => res.json())
            .map(result => {
                let rval = [];
                for (let idx = 0; idx < result.pieces.length; idx++) {
                    rval.push({name: result.pieces[idx].name, url: result.pieces[idx].image_urls[0]});
                }
                return rval;
            });
    }
}
