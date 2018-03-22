var cx = require('classnames')

var ShareItem = React.createClass({

  getUrl: function () {
    var url = []
    var urlConfig = this.props.urlConfig

    // 生成分享 URL
    for (var prop in urlConfig) {
      if (urlConfig.hasOwnProperty(prop)) {
        prop !== 'urlBase' ? url.push(prop + '=' + encodeURIComponent(urlConfig[prop])) : null
      }
    }
    url = urlConfig.urlBase + url.join('&')

    return url
  },

  render: function () {
    var classes = cx('share-btn', this.props.className)

    return (
      <a className={classes} href={this.getUrl()} target="_blank">{this.props.text}</a>
    )
  }
})

module.exports = ShareItem

