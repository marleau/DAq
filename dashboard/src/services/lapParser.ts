export class LapParser {
  private track: string;
  private splitLaps: any;
  private splitGeo = [
    {
      type: "LineString",
      coordinates: []
    }
  ];

  public parse() {
    let lap = 0;
    const temp = [];
    let track = undefined;
    const tempGeo = {
      type: "LineString",
      coordinates: []
    }
  }
}
