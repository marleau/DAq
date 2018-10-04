const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require("webpack");

module.exports = {
    entry: {
      app: "./src/app.tsx",
      vendor: ["react", "react-dom"],
    },
    output: {
        filename: "[name].bundle.js",
        path: path.resolve(__dirname, 'dist'),
    },
    devtool: "source-map",
    devServer: {
      contentBase: "./dist",
      // hot: true,
      compress: true,
    },
    resolve: {
      extensions: [".js", ".json", ".jsx", ".ts", ".tsx"]
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: "awesome-typescript-loader"
            },
            {
              test: /\.scss$/,
              use: [
                "style-loader", 
                "css-loader", 
                "sass-loader", 
              ]
            }
        ]
    },
    plugins: [
      new HtmlWebpackPlugin({template: path.resolve(__dirname, "public", "index.html")}),
      // new webpack.HotModuleReplacementPlugin(),
    ]
};