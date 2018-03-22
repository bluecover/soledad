// require('./mods/common/_load_svg_sprite')

require('lib/jquery.onemodal')
require('./common/_redeem')

require('mods/account/_account')
require('mods/common/back_top/_back_top')
require('mods/common/feedback/_feedback')
require('mods/common/_app_download_float')
require('mods/common/_csrf')
require('mods/common/_dropdown')
require('mods/common/_friend_link')
require('mods/common/_ga')
require('mods/common/_href')
require('mods/common/_mobile_nav')
require('mods/common/_notification')
require('mods/common/_progress_nav')
require('mods/common/_raven')
require('mods/common/_sidenav')
require('mods/common/svg_fallback')

if ($('.js-dlg-on-show').length) {
  $('.js-dlg-on-show').onemodal()
}
