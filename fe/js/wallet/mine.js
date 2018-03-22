let dlg_tips = require('mods/modal/modal_tips')
var moment = require('moment')
var dlg_error = require('g-error')

var tranItems = require('./mods/_tranItem.hbs')

var series_data = $('.js-profit-chart').data('amount')
var series_categories = $('.js-profit-chart').data('date')
series_data = series_data.map(function (item) {
  var d = {
    color: '#ddd',
    y: item
  }
  return d
})

if (series_data.length) {
  series_data[series_data.length - 1].color = '#6192b3'
}

function getWalletData(type) {
  $.ajax({
    url: '/j/wallet/available',
    type: 'GET',
    data: {
      order_type: type
    }
  }).done(function (c) {
    if (c.r) {
      window.location.href = c.data.redirect_url
    } else {
      let err_msg = '『' + c.error + '』'
      dlg_tips.show({
        tips_title: '温馨提示',
        tips_main: err_msg
      })
    }
  }).fail(function (res) {
    dlg_error.show(res && res.responseJSON && res.responseJSON.error)
  })
}

$('body')
  .on('click', '.js-btn-wallet', function () {
    let order_type = $(this).data('order-type')
    getWalletData(order_type)
  })
  .on('click', '.js-tips-close', function () {
    $(this).parents('.js-tips').slideUp('fast')
  })
new Highcharts.Chart({
  chart: {
    renderTo: $('.js-profit-chart')[0],
    type: 'column',
    height: '200'
  },
  credits: {
    enabled: false
  },
  title: false,
  xAxis: {
    categories: series_categories,
    tickWidth: 0
  },
  yAxis: {
    title: false,
    gridLineDashStyle: 'longdash'
  },
  tooltip: {
    formatter: function () {
      return this.series.name + ': ' + this.y + '元'
    }
  },
  legend: {
    enabled: false
  },
  plotOptions: {
    column: {
      pointPadding: 0.2,
      borderWidth: 0
    }
  },
  series: [{
    name: '收益',
    data: series_data
  }]
})

var annual_rates = $('.js-seven-chart').data('annual-rates')
var max_rate = -Infinity
var min_rate = Infinity
annual_rates.map(function (arry) {
  arry[0] = moment.utc(arry[0], 'YYYY-MM-DD').valueOf()
  arry[1] < min_rate ? min_rate = arry[1] : null
  arry[1] > max_rate ? max_rate = arry[1] : null
})

var seven_chart = new Highcharts.Chart({
  chart: {
    renderTo: $('.js-seven-chart')[0],
    type: 'area',
    marginTop: 40
  },
  credits: {
    enabled: false
  },
  legend: {
    enabled: false
  },
  title: {
    text: '七日年化收益率',
    floatting: true,
    align: 'left',
    style: {
      color: '#666',
      fontSize: '14px'
    },
    x: 0,
    y: 20
  },
  tooltip: {
    shadow: false,
    backgroundColor: '#6192b3',
    borderColor: '#6192b3',
    borderWidth: 1,
    borderRadius: 5,
    style: {
      color: '#fff'
    },
    formatter: function () {
      return moment(this.x).format('MM-DD') + '<br />' + this.y + '%'
    }
  },
  xAxis: {
    title: false,
    tickWidth: 0,
    lineWidth: 0,
    labels: {
      enabled: false
    }
  },
  yAxis: {
    title: false,
    gridLineWidth: 0,
    labels: {
      enabled: false
    },
    min: min_rate - (max_rate - min_rate),
    tickInterval: 0.01,
    max: max_rate
  },
  plotOptions: {
    area: {
      lineColor: '#6192b3',
      marker: {
        enabled: false,
        states: {
          hover: {
            fillColor: '#6192b3',
            lineColor: '#6192b3',
            lineWidthPlus: 1,
            radiusPlus: 1
          }
        }
      },
      fillOpacity: 0.7,
      fillColor: '#eee',
      threshold: -10
    }
  },
  series: [{
    data: annual_rates
  }]
})

try {
  var tip_length = seven_chart.series[0].points.length
  seven_chart.tooltip.refresh(seven_chart.series[0].points[tip_length - 1])
} catch (e) {}

var $recordTableBd = $('.js-record-table-bd')
var $loading = $('.js-icon-loading')
var $btnMore = $('.js-btn-more')

var transactions = []
var start_index = 5
var limit_num = 10
var urlParam = {
  start: start_index,
  limit: limit_num
}

if ($btnMore.length) {
  $('.js-btn-more').click(function (e) {
    var that = this

    $loading.show()
    $btnMore.addClass('btn-disable')

    $.ajax({
      type: 'GET',
      url: '/j/wallet/transactions',
      data: urlParam
    }).done(function (c) {

      $loading.hide()
      $btnMore.removeClass('btn-disable')

      if (c.r) {
        transactions = c.data.collection
        transactions.forEach(function (item, index) {
          item.type === 'deposit' ? item.isDeposit = true : item.isDeposit = false
        })
        $recordTableBd.append(tranItems({
          transactions: transactions
        }))

        urlParam.start += 10
        if (urlParam.start >= c.data.total) {
          $(that).remove()
        }
      } else if (c.error) {
        dlg_error.show(c.error)
      } else {
        dlg_error.show()
      }

    }).fail(function () {
      $loading.hide()
      $btnMore.removeClass('btn-disable')

      dlg_error.show()
    })

  })
}
