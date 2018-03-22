var path = require('path')
var glob = require('globby')
var JS_PATH = path.join(__dirname, 'fe/js')
var webpack = require('webpack')

function getEntries() {
  var map = {}
  var fileList = glob.sync(['./fe/js/**/*.js',
                           '!./fe/js/**/_*.js',
                           '!./fe/js/lib/**/*.js',
                           '!./fe/js/utils/**/*.js',
                           '!./fe/js/mods/**/*.js'])

  fileList.forEach(function (file) {
    var name = path.basename(file)
    var filePath = path.relative(JS_PATH, file)
    if (name.match(/^[^_](.+)\.js$/)) {
      map[filePath] = file
    }
  })

  return map
}

module.exports = {
  context: __dirname,
  entry: getEntries(),
  output: {
    path: path.join(__dirname, 'jupiter/static/build/webpack'),
    filename: '[name]'
  },
  module: {
    loaders: [{
      test: /\.jsx?$/,
      loader: 'babel-loader',
      exclude: /node_modules/,
      query: {
        // plugins: ['syntax-object-rest-spread',
          // 'transform-es3-member-expression-literals',
          // 'transform-es3-property-literals'],
        // presets: ['es2015', 'react'],
        cacheDirectory: true
      }
    }, {
      test: /\.hbs/,
      loader: 'handlebars-loader'
    // }, {
      // test: /\.js$/,
      // loader: 'es3ify'
    }]
  },
  resolve: {
    root: JS_PATH,
    alias: {
      'g-loading$': 'mods/modal/loading.js',
      'g-error$': 'mods/modal/error.js'
    }
  },
  plugins: [
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'production')
      }
    })
    // new webpack.optimize.UglifyJsPlugin({
      // compress: {
        // warnings: false
      // }
    // })
  ],
  devtool: '#inline-source-map',
  externals: {
    'jquery': '$',
    'react': 'React'
  }
}
