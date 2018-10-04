import { csvParse } from "d3-dsv";
import { RowData, GeoObject, TrackInfo } from "../interfaces";
import { Tracks } from "../tracks/tracks";
// import {time} from "d3-time";
// const timeFormatter = time.format("%H:%M:%S.%L");

export class LapParser {
  private track: TrackInfo;
  private splitLaps: any;
  private geo: GeoObject = {
    type: "LineString",
    coordinates: []
  };
  private splitGeo: GeoObject[] = [
    {
      type: "LineString",
      coordinates: []
    }
  ];
  private data: RowData[];

  public parse(file: string) {
    this.data = csvParse<RowData>(file, (d) => {
      this.geo.coordinates.push([Number(d.gpsLon), Number(d.gpsLat)]);
      return {
        // time: timeFormatter.parse(d.time.replace(/(\.[0-9]{3})[0-9]*/, "$1")),
        engineLoad: Number(d.engineLoad),
        coolantTemp: Number(d.coolantTemp),
        rpm: Number(d.rpm),
        speed: Number(d.speed),
        intakeTemp: Number(d.intakeTemp),
        maf: Number(d.maf),
        throttlePos: Number(d.throttlePos),
        timingAdvance: Number(d.timingAdvance),
        xG: Number(d.xG),
        yG: Number(d.yG),
        zG: Number(d.zG),
        gpsSpeed: Number(d.gpsSpeed),
        gpsLat: Number(d.gpsLat),
        gpsLon: Number(d.gpsLon),
        gpsAlt: Number(d.gpsAlt),
        gpsClimb: Number(d.gpsClimb)
      };
    });

    this.findTrack();
  }

  private findTrack() {
    if (this.track != null) return;

    this.data.forEach(row => {
      const square = this.toGridSquare(row.gpsLat, row.gpsLon);
      Object.values(Tracks).forEach(track => {
        if (track.gridSQ.includes(square)) {
          this.track = track;
        }
      });
    });
  }

  private toGridSquare(lat: any, lon: any): string {
    var lat = -100.0;
    var lon = 0.0;
    var adjLat, adjLon, GLat, GLon, nLat, nLon, gLat, gLon, rLat, rLon;
    var U = 'ABCDEFGHIJKLMNOPQRSTUVWX'
    var L = U.toLowerCase();
    // support Chris Veness 2002-2012 LatLon library and
    // other objects with lat/lon properties
    // properties could be numbers, or strings
    function toNum(x) {
      if (typeof (x) === 'number') return x;
      if (typeof (x) === 'string') return parseFloat(x);
      // dont call a function property here because of binding issue
      throw "HamGridSquare -- toNum -- can not convert input: " + x;
    }
    if (typeof (lat) === 'object') {
      if (lat.length === 2) {
        lat = toNum(lat[0]);
        lon = toNum(lat[1]);
      } else if (('lat' in lat) && ('lon' in lat)) {
        lat = (typeof (lat.lat) === 'function') ? toNum(lat.lat()) : toNum(lat.lat);
        lon = (typeof (lat.lon) === 'function') ? toNum(lat.lon()) : toNum(lat.lon);
      } else if (('latitude' in lat) && ('longitude' in lat)) {
        lat = (typeof (lat.latitude) === 'function') ? toNum(lat.latitude()) : toNum(lat.latitude);
        lon = (typeof (lat.longitude) === 'function') ? toNum(lat.longitude()) : toNum(lat.longitude);
      } else {
        throw "HamGridSquare -- can not convert object -- " + lat;
      }
    } else {
      lat = toNum(lat);
      lon = toNum(lon);
    }
    if (isNaN(lat)) throw "lat is NaN";
    if (isNaN(lon)) throw "lon is NaN";
    if (Math.abs(lat) === 90.0) throw "grid squares invalid at N/S poles";
    if (Math.abs(lat) > 90) throw "invalid latitude: " + lat;
    if (Math.abs(lon) > 180) throw "invalid longitude: " + lon;
    adjLat = lat + 90;
    adjLon = lon + 180;
    GLat = U[Math.trunc(adjLat / 10)];
    GLon = U[Math.trunc(adjLon / 20)];
    nLat = '' + Math.trunc(adjLat % 10);
    nLon = '' + Math.trunc((adjLon / 2) % 10);
    rLat = (adjLat - Math.trunc(adjLat)) * 60;
    rLon = (adjLon - 2 * Math.trunc(adjLon / 2)) * 60;
    gLat = L[Math.trunc(rLat / 2.5)];
    gLon = L[Math.trunc(rLon / 5)];
    return GLon + GLat + nLon + nLat + gLon + gLat;
  }
}