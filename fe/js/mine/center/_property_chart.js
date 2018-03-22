var $pie = $('.js-chart-property-pie')
var data = []

$('.js-pie-item').each(function (index, item) {
  var single = {}
  single.y = $(item).data('num') || 0
  single.color = $(item).css('background-color')
  data.push(single)
})

new Highcharts.Chart({
  chart: {
    renderTo: $pie[0],
    plotBackgroundColor: null,
    plotBorderWidth: null,
    plotShadow: false,
    backgroundColor: '#f3f9ff',
    margin: [0, 0, 0, 0]
  },
  credits: { enabled: false },
  title: { text: '' },
  tooltip: {enabled: false},
  plotOptions: {
    pie: {
      allowPointSelect: false,
      dataLabels: {enabled: false},
      size: '100%',
      innerSize: '70%',
      showInLegend: false,
      states: {
        hover: false
      }
    }
  },
  series: [{
    type: 'pie',
    name: 'percentage',
    data: data
  }]
})
