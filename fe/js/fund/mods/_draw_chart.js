function convert_percent(num) {
  num = Number(Number(num * 100).toFixed(2))
  return num
}

module.exports = function (c, element) {
  var time_arr = []
  var income_arr = []
  var stock_arr = []
  var datas = []

  $.each(c.data, function (key, value) {
    time_arr.push(value['day'])
    income_arr.push(value['income'])
    stock_arr.push(value['income_stock'])
    datas.push({
      date: time_arr[key],
      income: convert_percent(income_arr[key]),
      stock: convert_percent(stock_arr[key])
    })
  })

  AmCharts.makeChart(element, {
    'type': 'serial',
    'legend': {
      'useGraphSettings': true,
      'valueText': ''
    },
    'dataProvider': datas,
    'valueAxes': [{
      'axisAlpha': 0,
      'position': 'left'
    }],
    'graphs': [{
      'valueAxis': 'v1',
      'lineColor': '#FF6600',
      'bullet': 'round',
      'bulletBorderThickness': 1,
      'hideBulletsCount': 30,
      'title': c.group_subject,
      'valueField': 'income',
      'fillAlphas': 0,
      'balloonText': c.group_subject + ': [[income]]%'
    }, {
      'valueAxis': 'v2',
      'lineColor': '#FCD202',
      'bullet': 'round',
      'bulletBorderThickness': 1,
      'hideBulletsCount': 30,
      'title': '上证指数',
      'valueField': 'stock',
      'fillAlphas': 0,
      'balloonText': '上证指数: [[stock]]%'
    }],
    'marginLeft': 40,
    'chartCursor': {
      'categoryBalloonDateFormat': 'YYYY/MM/DD',
      'graphBulletSize': 1.5,
      'selectWithoutZooming': true,
      'zoomable': false
    },
    'dataDateFormat': 'YYYY-MM-DD',
    'categoryField': 'date',
    'categoryAxis': {
      'parseDates': true,
      'dateFormats': [{
        'period': 'DD',
        'format': 'DD'
      }, {
        'period': 'MM',
        'format': 'MM/DD'
      }, {
        'period': 'YYYY',
        'format': 'YYYY'
      }],
      'gridPosition': 'start',
      'fillColor': '#000000',
      'gridAlpha': 0,
      'position': 'bottom'
    }
  })
}
