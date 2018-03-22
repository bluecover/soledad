var gulp       = require('gulp')
var stylus     = require('gulp-stylus')
var nib        = require('nib')
var mincss     = require('gulp-cssnano')
var replace    = require('gulp-replace')
var plumber    = require('gulp-plumber')
var include    = require('gulp-include')
var gulpif     = require('gulp-if')
var jeet       = require('jeet')
var sourcemaps = require('gulp-sourcemaps')
var cache      = require('gulp-cached')
var livereload = require('gulp-livereload')
var svginline  = require('./svginline')

//var base64 = require('./base64')

var REGEX = global.REGEX
var REG_BUILD = global.REG_BUILD
var IMG_FILE = global.IMG_FILE

gulp.task('base-js', function() {
  return gulp.src('fe/js/lib/*.js')
             .pipe(include())
             .pipe(gulp.dest('jupiter/static/build/js/lib'))
})

gulp.task('build-img', function() {
  return gulp.src(IMG_FILE)
             .pipe(gulpif(!global.is_production, cache()))
             .pipe(gulp.dest('jupiter/static/build/img'))
})

gulp.task('build-stylus', function() {
  return gulp.src(['fe/css/**/*.styl', '!fe/css/**/_*.styl'])
             .pipe(gulpif(!global.is_production, cache()))
             .pipe(gulpif(!global.is_production, plumber()))
             .pipe(gulpif(!global.is_production, sourcemaps.init()))
             .pipe(stylus({use: [nib(), jeet()], 'include css': true}))
             .pipe(gulpif(!global.is_production, sourcemaps.write()))
             .pipe(gulpif(global.is_production, mincss({safe: true}), replace(REGEX, REG_BUILD)))
             .pipe(gulp.dest('jupiter/static/build/css'))
})

gulp.task('build-html', function() {
  return gulp.src('fe/html/**/*.html')
             .pipe(gulpif(!global.is_production, cache()))
             .pipe(svginline({basePath: './fe'}))
             .pipe(gulpif(!global.is_production, replace(REGEX, REG_BUILD)))
             .pipe(gulpif(!global.is_production, gulp.dest('jupiter/templates'), gulp.dest('jupiter/static/build/html')))
             .pipe(gulpif(!global.is_production, livereload()))
})

gulp.task('webpack-js', function() {
  return gulp.src('jupiter/static/build/webpack/**/*.js')
             .pipe(gulpif(!global.is_production, cache()))
             .pipe(svginline({basePath: './fe'}))
             .pipe(gulpif(!global.is_production, replace(REGEX, REG_BUILD)))
             .pipe(gulp.dest('jupiter/static/build/js'))
             .pipe(gulpif(!global.is_production, livereload()))
})

//gulp.task('base64', function() {
  //return gulp.src('fe/html/**/*.html')
             //.pipe(base64({basePath:'./fe'}))
//})
