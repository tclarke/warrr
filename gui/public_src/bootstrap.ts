import {platformBrowserDynamic} from "@angular/platform-browser-dynamic";
import {HttpModule, JsonpModule} from "@angular/http";
import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {MaterialModule} from "@angular/material";
import {BrowserModule} from "@angular/platform-browser";
import {AppComponent} from "./components/app/app.component";
import {NavigatorComponent} from "./components/navigator/navigator.component";
import {MarkerComponent} from "./components/marker/marker.component";
import {MapService} from "./services/map.service";
import {MarkerService} from "./services/marker.service";
import {GeocodingService} from "./services/geocoding.service";

@NgModule({
    imports:      [HttpModule,
        FormsModule,
        JsonpModule,
        BrowserModule,
        MaterialModule.forRoot()
    ],
    bootstrap:    [AppComponent],
    declarations: [
        AppComponent,
        NavigatorComponent,
        MarkerComponent
    ],
    providers:    [
        MapService,
        GeocodingService,
        MarkerService
    ]
})

export class AppModule {
}

platformBrowserDynamic().bootstrapModule(AppModule);
