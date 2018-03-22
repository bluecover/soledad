$(function () {
  var content = $('#contract_data').data('contract')

  var $iframe = $('<iframe></iframe>')
  $('body').append($iframe)
  var iframeDoc = $iframe[0].contentDocument || $iframe[0].contentWindow.document
  iframeDoc.write(content)
  iframeDoc.close()
  $('#contract').append($iframe.contents().find('.container'))
  $iframe.remove()
})
