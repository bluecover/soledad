/**
 * created by mindspop on 8/6/15.
 */

var gulp = require('gulp')
var imagemin = require('gulp-imagemin')
var svg2png = require('gulp-svg2png')
//var svgstore = require('gulp-svgstore')
//var cheerio = require('gulp-cheerio')
//var rename = require('gulp-rename')

// svg 转成 png
gulp.task('svg2png', function () {
  return gulp.src(['fe/img/**/*.svg', '!fe/img/font/**/*.svg'])
    .pipe(svg2png(2))
    .pipe(imagemin())
    .pipe(gulp.dest('jupiter/static/build/img'))
})

// 合并多个通用 svg
//gulp.task('svgSprite', function () {

  //return gulp.src('fe/img/common_svg_icon/**/*.svg')
      //.pipe(svgstore())
      //.pipe(cheerio(function($) {
        //$('svg').attr('style', 'display: none')
      //}))
      //.pipe(rename('common_icon.svg'))
      //.pipe(gulp.dest('jupiter/static/build/img/common_svg_icon'))
//})

// 如果要执行 svgSprite，需要把它加入 task
gulp.task('svg', ['svg2png'])
