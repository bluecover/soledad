var ShareWeixin = require('./_shareWeixin.jsx')
var ShareItem = require('./_shareItem.jsx')
var objectAssign = require('object-assign')

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
  // 分享理由
  desc: '',
  // 分享图片地址, 多张图片可以使用「||」分隔，示例：'a.jpg||b.jpg'
  pic: '',
  // 第三方 AppKey，示例 {tsina: '11111', qzone:'1112'}
  appkey: {},
  // @相关账号
  ralateUid: '',
  // 分享尾部信息
  site: '好规划'
}

// 需要分享的渠道，按配置顺序依次显示，示例[{tsina: ''}, {qq: ''}, {weixin: ''}]
// 若显示文案名称，配置规则：[{tsian: '分享到新浪微博'}, {qq: '分享到QQ'}]
var snsDefaultShow = [{weixin: ''}, {tsina: ''}, {qzone: ''}]

// 微信分享二维码配置信息
var weixinDefaultConfig = {
  title: '微信分享二维码',
  desc: '打开手机微信，选择「微信」标签，点击右上角「+」，选择「扫一扫」。',
  // 二维码图片地址
  picUrl: ''
}

var ShareList = React.createClass({

  generateShareList: function (snsShow) {
    var shareBtns = []

    // 提取微信配置
    this.weixinConfig = objectAssign({}, weixinDefaultConfig, this.props.shareConfig.weixin || {})

    var userConfig = this.props.shareConfig
    var generalConfig = objectAssign({}, defaultConfig, userConfig.general)

    // 依次配置每一个分享按钮
    for (var i = 0, len = snsShow.length; i < len; i++) {
      for (var sns in snsShow[i]) {

        // 获取分享渠道配置信息
        var shareConfig = objectAssign({}, generalConfig, userConfig[sns] || {})
        // 只有新浪微博支持多张图片
        sns !== 'tsina' ? shareConfig.pic.split('||')[0] : null
        // 获取分享渠道按钮名称，默认为空
        var snsText = snsShow[i][sns]

        // 按照 snsShow 设定的顺序生成分享按钮列表
        shareBtns.push(this.generateShareItem(sns, snsText, shareConfig))
      }
    }

    return shareBtns
  },

  generateShareItem: function (sns, snsText, shareConfig) {
    var urlData
    var shareItem

    if (sns !== 'weixin') {
      urlData = generateUrlConfig(sns, shareConfig)
      shareItem = <ShareItem urlConfig={urlData} text={snsText} className={'btn-' + sns}/>
    } else {
      shareItem = <ShareWeixin data={this.weixinConfig} text={snsText}/>
    }

    return shareItem
  },

  render: function () {
    // 获取分享按钮数量和顺序信息
    var snsShow = this.props.shareConfig.snsShow || snsDefaultShow

    return (
      <div id="share-list" className="share-btns">
        {this.generateShareList(snsShow)}
      </div>
    )
  }
})

function generateUrlConfig(sns, shareConfig) {
  var urlData = {
    tsina: {
      urlBase: 'http://service.weibo.com/share/share.php?',
      url: shareConfig.url,
      title: shareConfig.title,
      source: shareConfig.site,
      content: shareConfig.summary,
      pic: shareConfig.pic,
      appkey: (shareConfig.appkey.share || ''),
      ralateUid: shareConfig.ralateUid,
      searchPic: shareConfig.searchPic
    },

    qzone: {
      urlBase: 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?',
      url: shareConfig.url,
      site: shareConfig.site,
      title: shareConfig.title,
      summary: shareConfig.summary,
      pics: shareConfig.pic,
      appkey: (shareConfig.appkey.share || ''),
      desc: shareConfig.desc
    },

    qq: {
      urlBase: 'http://connect.qq.com/widget/shareqq/index.html?',
      url: shareConfig.url,
      title: shareConfig.title,
      pics: shareConfig.pic,
      summary: shareConfig.summary,
      desc: shareConfig.desc,
      site: shareConfig.site
    },

    douban: {
      urlbase: 'http://www.douban.com/share/service?',
      href: shareConfig.url,
      name: shareConfig.title,
      text: shareConfig.summary
    },

    renren: {
      urlBase: 'http://widget.renren.com/dialog/share?',
      link: shareConfig.url,
      title: shareConfig.title,
      content: shareConfig.summary,
      images: shareConfig.pic
    }
  }

  return urlData[sns]
}

module.exports = ShareList

