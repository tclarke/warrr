import {Component, ViewChild} from "@angular/core";
import {MarkerComponent} from "../marker/marker.component";
import {Board} from "../../core/board.class";
import {BoardService} from "../../services/board.service";
import {MarkerService} from "../../services/marker.service";
import {MapService} from "../../services/map.service";
import {GeocodingService} from "../../services/geocoding.service";

@Component({
    selector:  "app",
    template:  require<any>("./app.component.html"),
    styles:    [
        require<any>("./app.component.less")
    ],
    providers: []
})
export class AppComponent {
    board: Board;

    @ViewChild(MarkerComponent) markerComponent: MarkerComponent;

    constructor(private markerService: MarkerService,
                private boardService: BoardService,
                private mapService: MapService,
                private geocoder: GeocodingService) {
        this.board = null;
    }

    ngOnInit() {
        let map = L.map("map", {
            zoomControl: false,
            center:      L.latLng(40.731253, -73.996139),
            zoom:        12,
            minZoom:     4,
            maxZoom:     19,
            layers:      [this.mapService.baseMaps.Outdoors]
        });

        L.control.zoom({position: "topright"}).addTo(map);
        L.control.layers(this.mapService.baseMaps).addTo(map);
        L.control.scale().addTo(map);

        this.mapService.map = map;
        this.geocoder.getCurrentLocation()
            .subscribe(
                location => map.panTo([location.latitude, location.longitude]),
                err => console.error(err)
            );
    }

    ngAfterViewInit() {
        this.markerComponent.Initialize();
    }

    saveBoardState() {
        if (this.board === null) {
            this.boardService.createBoard()
                .subscribe(board => {
                    this.board = board;
                    this.board.saveState().subscribe(board => {
                    });
                });
        } else {
            this.board.saveState().subscribe(board => {
            });
        }
    }
}
