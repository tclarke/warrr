import {Component, ElementRef, Renderer, ViewEncapsulation} from "@angular/core";
import {MapService} from "../../services/map.service";
import {Map, MouseEvent, Marker} from "leaflet";

@Component({
    selector:      "marker",
    template:      require<any>("./marker.component.html"),
    styles:        [
        require<any>("./marker.component.less"),
        require<any>("../../styles/main.less")
    ],
    providers:     [],
    encapsulation: ViewEncapsulation.None
})
export class MarkerComponent {
    markerCount: number;
    inputMode: string;
    markerUrl: string;
    markerTypes = [
        {name:   "foo",
            url: "https://upload.wikimedia.org/wikipedia/commons/e/e3/NATO_Map_Symbol_-_Headquarters_Unit.svg"
        },
        {name:   "bar",
            url: "https://upload.wikimedia.org/wikipedia/commons/2/23/NATO_Map_Symbol_-_Infantry_%28Light%29.svg"
        },
        {name:   "ack ick",
            url: "https://upload.wikimedia.org/wikipedia/commons/3/39/NATO_Map_Symbol_-_Mounted_Infantry.svg"
        },
    ];

    constructor(private el: ElementRef, private renderer: Renderer, private mapService: MapService) {
        this.markerCount = 0;
        this.inputMode = "";
        this.markerUrl = "";
    }

    ngOnInit() {
        this.renderer.setElementStyle(this.el.nativeElement, "backgroundColor", "yellow");
    }

    Initialize() {
        this.mapService.map.on("click", (e: MouseEvent) => {
            if (this.inputMode == "friendly" || this.inputMode == "neutral" || this.inputMode == "hostile") {
                let marker = L.marker(e.latlng, {
                    icon:      L.icon({
                        iconSize:  [50, -1],
                        iconUrl:   this.markerUrl,
                        className: ("marker-" + this.inputMode)
                    }),
                    draggable: true
                })
                    .bindPopup("Marker #" + (this.markerCount + 1).toString(), {
                        offset: L.point(12, 6)
                    })
                    .addTo(this.mapService.map)
                    .openPopup();

                this.markerCount += 1;

                marker.on("click", (event: MouseEvent) => {
                    if (this.inputMode == "remove") {
                        this.mapService.map.removeLayer(marker);
                        this.markerCount -= 1;
                    }
                });
            }
        });
    }
}
