var fs         = require('fs')
var gulp       = require('gulp')
var stylus     = require('gulp-stylus')
var gulpif     = require('gulp-if')
var watch      = require('gulp-watch')
var plumber    = require('gulp-plumber')
var nib        = require('nib')
var replace    = require('gulp-replace')
var liveload   = require('gulp-livereload')
var jeet       = require('jeet')
var sourcemaps = require('gulp-sourcemaps')
var browserify = require('./browserify')

var REGEX = global.REGEX
var REG_BUILD = global.REG_BUILD
var IMG_FILE = global.IMG_FILE

gulp.task('watchify', function() {
  var is_dev = true
  return browserify(is_dev)
})

var css_path = 'fe/css'
var dirs = fs.readdirSync(css_path)
var STYLUS_TASKS = []

dirs.forEach(function(item) {
  if(fs.statSync(css_path+'/'+item).isDirectory()) {
    STYLUS_TASKS.push(item)
  }
})

for(var i=0; i<STYLUS_TASKS.length; i++) {
  (function(i) {
    gulp.task('build-stylus-' + STYLUS_TASKS[i], function() {
      return gulp.src(['fe/css/' + STYLUS_TASKS[i] + '/*.styl', '!fe/css/' + STYLUS_TASKS[i] + '/_*.styl'])
      .pipe(gulpif(!global.is_production, plumber()))
      .pipe(gulpif(!global.is_production, sourcemaps.init()))
      .pipe(stylus({use: [nib(), jeet()], 'include css': true}))
      .pipe(gulpif(!global.is_production, sourcemaps.write()))
      .pipe(replace(REGEX, REG_BUILD))
      .pipe(gulp.dest('jupiter/static/build/css/'+STYLUS_TASKS[i]))
      .pipe(liveload())
    })
  })(i)
}

gulp.task('dev', ['webpack-js', 'base-js', 'build-stylus', 'build-html', 'build-img'], function() {
  global.is_production = false
  liveload.listen()

  for(var i=0; i<STYLUS_TASKS.length; i++) {
    (function(i) {
      watch('fe/css/' + STYLUS_TASKS[i] +'/**/*.styl', function() {
        gulp.start('build-stylus-'+STYLUS_TASKS[i])
      })
    })(i)
  }

  watch('fe/js/lib/*.js', function() {
    gulp.start('base-js')
  })

  watch('jupiter/static/build/webpack/**/*.js', function() {
    gulp.start('webpack-js')
  })

  watch('fe/html/**/*.html', function() {
    gulp.start('build-html')
  })

  watch(IMG_FILE, function() {
    gulp.start('build-img')
  })

  // 监听合并 SVG
  //watch('fe/img/common_svg_icon/**/*.svg', function() {
    //gulp.start('svgSprite')
  //})
})
