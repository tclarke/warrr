/**
 * Created by tclarke on 11/14/16.
 */
var map = L.map('gamemap').setView([50.690833,4.406111], 13);
L.tileLayer('http://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey={apikey}', {
	attribution: '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
	apikey: '03bcc0f8a1d840fc90a79ba42b51b9ce'
}).addTo(map);