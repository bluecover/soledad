var gutil = require('gulp-util')
var through = require('through2')
var fs = require('fs')
var path = require('path')
var objectAssign = require('object-assign')

var defaultOptions = {
  regex: /\{base64\{\{(\S*?)\}\}\}/g,
  basePath: './'
}

module.exports = function(options) {
  var opt = objectAssign({}, defaultOptions, options)

  return through.obj(function(file, encoding, callback) {
    if (file.isNull()) {
      this.push(file)
      return callback()
    }

    if (file.isStream()) {
      this.emit('error', new gutil.PluginError('gulp-base64', 'Streaming not supported'))
      return callback()
    }

    if (file.isBuffer()) {
      var output = String(file.contents)
      output = output.replace(opt.regex, function(match, p1) {
        var imgPath = path.join(opt.basePath, p1)
        var imgFile = fs.readFileSync(imgPath)
        var imgBase64 = new Buffer(imgFile).toString('base64')
        return imgBase64
      })
      file.contents = new Buffer(output)
      return callback(null, file)
    }
  })
}
