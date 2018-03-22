var gulp = require('gulp')
var eslint = require('gulp-eslint')

gulp.task('eslint', function () {
  return gulp.src(['fe/js/**/*.js',
                  'fe/js/**/*.jsx',
                  '!node_modules/**',
                  '!fe/js/lib/**/*.js'])
             .pipe(eslint())
             .pipe(eslint.format())
             .pipe(eslint.failAfterError())
})
