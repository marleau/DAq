export interface RowData {
  // time;
  engineLoad?: number;
  coolantTemp?: number;
  rpm?: number;
  speed?: number;
  intakeTemp?: number;
  maf?: number;
  throttlePos?: number;
  timingAdvance?: number;
  xG?: number;
  yG?: number;
  zG?: number;
  gpsSpeed?: number;
  gpsLat?: number;
  gpsLon?: number;
  gpsAlt?: number;
  gpsClimb?: number;
}

export interface GeoObject {
  type: string;
  coordinates: GeoCoordinates[];
}

export type GeoCoordinates = number[];

export interface TrackInfo {
  name: string;
  gridSQ: string[];
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  geojson: string;
}