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
    friendly: boolean;
    neutral: boolean;
    hostile: boolean;
    removing: boolean;
    markerCount: number;

    constructor(private el: ElementRef, private renderer: Renderer, private mapService: MapService) {
        this.friendly = false;
        this.neutral = false;
        this.hostile = false;
        this.removing = false;
        this.markerCount = 0;
    }

    ngOnInit() {
        this.mapService.disableMouseEvent("add-friendly");
        this.mapService.disableMouseEvent("add-neutral");
        this.mapService.disableMouseEvent("add-hostile");
        this.mapService.disableMouseEvent("remove-marker");
        this.renderer.setElementStyle(this.el.nativeElement, "backgroundColor", "yellow");
    }

    Initialize() {
        this.mapService.map.on("click", (e: MouseEvent) => {
            if (this.friendly || this.neutral || this.hostile) {
                let marker = L.marker(e.latlng, {
                    icon:      L.icon({
                        iconSize:  [50, -1],
                        iconUrl:   "https://upload.wikimedia.org/wikipedia/commons/2/23/NATO_Map_Symbol_-_Infantry_%28Light%29.svg",
                        className: (this.friendly ? "markerFriendly" : (this.neutral ? "markerNeutral" : (this.hostile ? "markerHostile" : "")))
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
                    if (this.removing) {
                        this.mapService.map.removeLayer(marker);
                        this.markerCount -= 1;
                    }
                });
            }
        });
    }

    toggleFriendly() {
        this.friendly = !this.friendly;
        this.neutral = this.hostile = this.removing = false;
    }

    toggleNeutral() {
        this.neutral = !this.neutral;
        this.friendly = this.hostile = this.removing = false;
    }

    toggleHostile() {
        this.hostile = !this.hostile;
        this.friendly = this.neutral = this.removing = false;
    }

    toggleRemoving() {
        this.removing = !this.removing;
        this.friendly = this.neutral = this.hostile = false;
    }
}
