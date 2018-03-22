var reqdir  = require('require-dir')

global.REGEX = /\{\{\{(\S*?)\}\}\}/g
global.REG_BUILD = '/static/build/$1'
global.MANIFEST =  __dirname + '/jupiter/static/rev-manifest.json'
global.DIST_DIR = JSON.parse(process.env.SOLAR_ASSETS_QINIU_URL || '"/static/dist/"')


global.IMG_FILE = 'fe/img/**/*.+(png|gif|jpg|eot|woff|ttf|svg|ico)'
global.JS_FILE = ['fe/js/**/*.js',
                  '!fe/js/**/*.jsx',
                  '!fe/js/mods/**/*.js',
                  '!fe/js/lib/**/*.js',
                  '!fe/js/utils/**/*.js',
                  '!fe/js/**/_*.js']

reqdir('./fe/gulp/')
