import loading_dlg from 'mods/redirect_dlg/_loading_dlg.js'
import products_list from './mods/_ins_product_data.js'

const tmpl_product_list = require('./mods/_products_list.hbs')
const products_doms = new Map()

let $slideWrapper = $('.ins-slide-wrapper')

// 点击保险介绍，动画显示产品详情
$('.m-ins-intro').on('click', function (e) {
  let name = $(this).data('name')
  let $dom = products_doms.get(name)

  // 保存模板结果，避免重复渲染
  if (!$dom) {
    $dom = $(tmpl_product_list(products_list[name]))
    products_doms.set(name, $dom)
  }

  $slideWrapper
    .empty()
    .append($dom)
    .css({
      minHeight: window.innerHeight
    })
    .removeClass('ins-detail-hide')
    .addClass('ins-detail-show')
})

// 点击返回按钮，回到保险介绍主页
$('body').on('click', '.btn-back', function (e) {
  $slideWrapper.addClass('ins-detail-hide').removeClass('ins-detail-show')
})

// 处理产品详情跳转链接
$('body').on('click', '.m-ins-product', function (e) {
  let $price = $(this).find('.price')
  let ins_title = $(this).find('.bd .title').html()
  let href = $price.attr('href')
  let external_url = $price.data('url')

  if (external_url) {
    e.preventDefault()

    loading_dlg.show({
      ins_title: ins_title,
      redirect_url: external_url,
      partner_logo_src: $price.data('partner-logo-src')
    })
  } else if (href) {
    window.open(href)
    return false
  }
})

// weixin share
let config = $('#ins_data').data('val')
let title = '保险精选 – 好规划'
let desc = '不会选保险？好规划帮你万里挑一'
let url = window.location.href

desc = {
  title: title,
  desc: desc,
  link: url,
  imgUrl: 'https://dn-ghimg.qbox.me/rMWePhOI5Uv0mNfR'
}
wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})
