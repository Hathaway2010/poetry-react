const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {
  entry: {
    index: ['./scansion/assets/index.js', './scansion/assets/styles.scss'], 
    layout: './scansion/assets/layout.scss',       
  }, 
  output: {
    filename: '[name].js',  // output bundle file name
    path: path.resolve(__dirname, './scansion/static/scansion'),  // path to our Django static directory
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: { presets: ["@babel/preset-env", "@babel/preset-react"] }
      },
      {
        test:/\.scss$/,
        exclude: /node_modules/,
        use: [
          // fallback to style-loader in development
          MiniCssExtractPlugin.loader,
          "css-loader",
          "sass-loader"
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
  ],
};