var yixin = $('<div class="onemodal">' +
                 '<div class="modal-dialog-hd">正在跳转至宜人贷授权页面...</div>' +
                 '<div class="modal-dialog-bd">宜人贷网下属于宜信公司，宜定盈是宜信公司推出的产品</div>' +
              '</div>')

$('body').append(yixin)

module.exports = {
  show: function () {
    yixin.onemodal({
      clickClose: false,
      escapeClose: false
    })
  },
  close: function () {
    $.onemodal.close()
  }
}
