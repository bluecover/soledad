;(function (factory) {

  if (typeof define === 'function' && define.amd) {
    // AMD 模式
    define(['jquery'], factory)
  } else if (typeof exports === 'object') {
    // CMD 模式
    factory(require('jquery'))
  } else {
    factory(jQuery)
  }

}(function ($) {
  if ($.fn.share) {
    return
  }

  // 分享配置信息
  var defaultConfig = {
    // 分享 URL
    url: window.location.href,
    // 分享标题
    title: document.title,
    // 是否允许新浪微博自动抓取图片
    searchPic: true,
    // 分享摘要
    summary: '',
    // 分享图片地址, 多张图片可以使用「||」分隔，示例：'a.jpg||b.jpg'
    pic: '',
    // 第三方 AppKey，示例 {tsina: '11111', qzone:'1112'}
    appkey: {},
    // @相关账号
    ralateUid: '',
    // 分享尾部信息
    site: '好规划'
  }

  // 分享接口配置，可以按如下格式添加新 API
  var defaultShareApi = {
    weixin: {
      title: '微信分享二维码',
      desc: '打开手机微信，选择「微信」标签，点击右上角「+」，选择「扫一扫」。',
      picUrl: ''
    },
    tsina: 'http://service.weibo.com/share/share.php?url={url}&source={site}&title={title}&content={summary}&pic={pic}&appkey={appkey}&ralateUid={ralateUid}&searchPic={searchPic}',
    qzone: 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url={url}&title={title}&desc={desc}&pics={pic}&summary={summary}&site={site}',
    qq: 'http://connect.qq.com/widget/shareqq/index.html?url={url}&title={title}&pics={pic}&summary={summary}&desc={desc}&site={site}',
    douban: 'http://www.douban.com/share/service?href={url}&name={title}&text={summary}',
    renren: 'http://widget.renren.com/dialog/share?link={url}&title={title}&pic={pic}'
  }

  // 解析第三方 API 对应的 URL
  function parseUrl(url, data) {
    var reg = /\{.+?\}/g
    url = url.replace(reg, function (match) {
      var prop = match.slice(1, -1)
      return encodeURIComponent(data[prop])
    })
    return url
  }

  var Share = function (ele, option, shareApi) {
    this.config = $.extend({}, defaultConfig, option || {})
    this.shareApi = $.extend({}, defaultShareApi, shareApi || {})
    this.$ele = $(ele)
    // 确保给分享组件的每一个分享按钮添加 share-btn class
    this.$list = this.$ele.find('.share-btn')
    this.init()
  }

  Share.prototype.init = function () {
    this.renderUrl(this.config)
  }

  Share.prototype.renderUrl = function (data) {
    var self = this
    var pics

    this.$list.each(function () {
      var $this = $(this)
      // 确保分享按钮附带 data-type 以标示正确的分享渠道，type 类型见 defaultShareApi
      var type = $this.data('type')
      var configCopy = $.extend({}, data)
      var appKeys

      if (self.shareApi[type] === undefined) {
        return
      }

      // 微信分享仅弹出二维码
      if (type === 'weixin') {
        $this.on('click', function () {
          var $qrcode = $('#qrcode-mod')
          $qrcode.length > 0 ? null : new Qrcode(self.shareApi.weixin)
          $qrcode.show()
        })
        return
      }

      if (type !== 'tsina') {
        pics = configCopy.pic.split('||')
        configCopy.pic = pics[0]
      }

      // 设置正确的 appKey
      appKeys = configCopy.appKey
      for (var sns in appKeys) {
        configCopy.appKey = appKeys[sns]
      }

      var url = self.shareApi[type]

      url = parseUrl(url, configCopy)
      // 给每一个分享按钮标签添加分享 URL 地址
      $this.attr('href', url)
    })
  }

  $.fn.share = function (option, shareApi) {
    this.each(function () {
      new Share(this, option, shareApi)
    })
    return this
  }

  // 微信二维码弹出层配置信息
  var qrConfig = {
    title: '微信分享二维码',
    desc: '打开手机微信，选择「微信」标签，点击右上角「+」，选择「扫一扫」。',
    picUrl: ''
  }

  var Qrcode = function (option) {
    this.config = $.extend({}, qrConfig, option || {})
    this.tmpl = '<div id="qrcode-mod" class="qrcode-mod">' +
      '<div class="hd"><h3 class="title">{title}</h3><a class="close-btn" href="#">&times;</a></div>' +
      '<div class="bd"><img class="qrcode-img" src="{picUrl}" /></div>' +
      '<div class="ft">{desc}</div>' +
      '</div>'

    this.init()
  }

  Qrcode.prototype.init = function () {
    this.render()
    this.bind()
  }

  Qrcode.prototype.render = function () {
    var tmpl = parseTemplate(this.tmpl, this.config)
    $('body').append(tmpl)
    $('#qrcode-mod').css({
      position: 'fixed',
      top: 0,
      left: 0,
      bottom: 0,
      right: 0,
      width: 300,
      height: 400,
      backgroundColor: '#fff',
      padding: '10px 25px',
      margin: 'auto'
    }).find('.qrcode-img').css({
      display: 'inline-block',
      width: 250,
      height: 250
    }).parent().parent() .find('.ft').css({
      lineHeight: 1.5,
      marginTop: 10
    }).parent().find('.close-btn').css({
      position: 'absolute',
      top: 10,
      right: 10,
      fontSize: 24
    })
  }

  // 绑定关闭二维码弹出层按钮事件
  Qrcode.prototype.bind = function () {
    var $qrcode = $('#qrcode-mod')
    $qrcode.find('.close-btn').on('click', function (e) {
      $qrcode.hide()
    })
  }

  function parseTemplate(tmpl, data) {
    var reg = /\{.+?\}/g
    tmpl = tmpl.replace(reg, function (match) {
      var prop = match.slice(1, -1)
      return data[prop]
    })
    return tmpl
  }

}))

