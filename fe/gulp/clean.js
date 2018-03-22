var gulp   = require('gulp');
var del = require('del')

gulp.task('clean', function(cb) {
  del(['jupiter/static/build',
      'jupiter/static/dist',
      'jupiter/static/tmp',
      'jupiter/templates',
      'jupiter/static/rev-manifest.json'
  ], cb)
})
