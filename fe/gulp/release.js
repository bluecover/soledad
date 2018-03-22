var rev        = require('gulp-rev')
var gulp       = require('gulp')
var uglify     = require('gulp-uglify')
var gutil      = require('gulp-util')
var replace    = require('gulp-replace')
var del        = require('del')
var browserify = require('./browserify')
var qiniu      = require('gulp-qiniu')
var ak         = JSON.parse(process.env.SOLAR_QINIU_AK || null)
var sk         = JSON.parse(process.env.SOLAR_QINIU_SK || null)

function replaceFunc(match, p1) {
  var manifest = require(global.MANIFEST)
  return global.DIST_DIR + manifest[p1]
}

gulp.task('browserify', function() {
  return browserify()
})

gulp.task('release-js', ['webpack-js',
          'base-js',
          'svg',
          'build-img',
          'build-stylus',
          'build-html'], function() {
  return gulp.src(['jupiter/static/build/js/**/*.js', '!jupiter/static/build/js/**/*.min.js'])
             .pipe(uglify().on('error', gutil.log))
             .pipe(gulp.dest('jupiter/static/build/js'))
})

gulp.task('release-rev', ['release-js'], function() {
  return gulp.src(['jupiter/static/build/css/**/*.css',
                   'jupiter/static/build/js/**/*.js',
                   'jupiter/static/build/img/**/*.+(png|gif|jpg|eot|woff|ttf|svg|ico)'],
                   {base: './jupiter/static/build'})
             .pipe(gulp.dest('jupiter/static/build/'))
             .pipe(rev())
             .pipe(gulp.dest('jupiter/static/dist'))
             .pipe(rev.manifest())
             .pipe(gulp.dest('jupiter/static'))
})

gulp.task('css-js-replace', ['release-rev'], function() {
  return gulp.src(['jupiter/static/dist/**/*.css', 'jupiter/static/dist/**/*.js'])
             .pipe(replace(global.REGEX, replaceFunc))
             .pipe(gulp.dest('jupiter/static/dist'))
})

gulp.task('html-replace', ['css-js-replace'], function() {
  return gulp.src('jupiter/static/build/html/**/*.html')
             .pipe(replace(global.REGEX, replaceFunc))
             .pipe(gulp.dest('jupiter/templates'))
})

gulp.task('set-release', function() {
  global.is_production = true
})

gulp.task('release', ['set-release', 'html-replace'], function(cb) {
  del(['jupiter/static/build'], cb)
  //上传七牛
  if(ak && sk) {
    return gulp.src('jupiter/static/dist/**')
      .pipe(qiniu({
        accessKey: ak,
        secretKey: sk,
        bucket: 'guihua-assets'
      }, {
        dir: '/'
      }))
  }
})
