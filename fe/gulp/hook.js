var gulp = require('gulp')
var symlink = require('gulp-symlink')
var path = require('path')

var precommit = path.resolve(__dirname, '../../.pre-commit')

function hook() {
  return gulp.src([precommit])
    .pipe(symlink(function () {
      return new symlink.File({
        cwd: process.cwd(),
        path: '.git/hooks/pre-commit'
      })
    }, {
      force: true
    }))
}

gulp.task('hook', hook)
