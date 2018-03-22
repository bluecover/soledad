var gulp       = require('gulp')
var browserify = require('browserify')
var watchify   = require('watchify')
var gutil      = require('gulp-util')
var reactify   = require('reactify')
var babelify   = require('babelify')
var through2   = require('through2')
var replace    = require('gulp-replace')
var assign     = require('object-assign')
var gulpif     = require('gulp-if')
var svginline  = require('./svginline')

var REGEX = global.REGEX
var REG_BUILD = global.REG_BUILD
var JS_FILE = global.JS_FILE

module.exports = function(is_dev) {
  var options = {
    paths: ['fe/js']
  }

  if(is_dev) {
    options = assign({}, options, {
      debug: true,
      cache: {},
      packageCache: {}
    })
  }

  var bundler = function() {
    return through2.obj(function(file, enc, next) {
      var b = browserify(file.path, options)
              .transform(babelify)
              .transform({
                global: true
              }, 'browserify-shim')

      if(is_dev) {
        b = watchify(b)
        b.on('update', bundle)
        b.pipeline.on('file', function(filename) {
          gutil.log(gutil.colors.green('Bundled: '), filename)
        })
      }

      return b.bundle(function(err, res) {
        if(err) {
          return next(err)
        }
        file.contents = res
        next(null, file)
      })
    })
  }

  function bundle() {
    is_dev ? gutil.log(gutil.colors.yellow('Bundling...')) : null
    return gulp.src(JS_FILE)
      .pipe(bundler())
      .on('error', function(e) {
        gutil.log(gutil.colors.red(e.message))
        is_dev ? this.emit('end') : null
      })
      .pipe(svginline({basePath: './fe'}))
      .pipe(gulpif(is_dev, replace(REGEX, REG_BUILD)))
      .pipe(gulp.dest('jupiter/static/build/js'))
  }

  return bundle()
}
