// plotly.js-dist-min ships no typings — it is the same API surface as plotly.js
// (which @types/plotly.js covers), just the prebuilt minified bundle. PlotlyChart
// feeds it to react-plotly.js/factory.
declare module "plotly.js-dist-min" {
  import * as Plotly from "plotly.js";
  export default Plotly;
}
