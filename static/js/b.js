
$(document).ready(function(e) {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('main'));

    var option = {
        title: {
            text: '总资产变化明细',
        },
        color: ['#C0392B','#9B59B6', '#2980B9', '#1ABC9C', '#F1C40F', '#E67E22', '#7F8C8D', '#34495E'],
        legend: {},
        tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        toolbox: {
            feature: { 
                //magicType: {type: ['stack', 'tiled']},
                saveAsImage: {} 
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                //data : ['周一','周二','周三','周四','周五','周六','周日']
                //data : ['1']
            }
        ],
        yAxis : [ { type : 'value' } ],
        series : [ ]
    };

    //// 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);

    var get_stat = function() {
        var stat_result = "#stat_result"
        $.ajax({  
            type: "get",  
            url: "/api/v1/statistics",
            //data: {'price': price, 'istype': istype},
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend: function() { 
                return true;
            },
            success: function(d) { 
                $(stat_result).html("<span></span>");
                if (d.result) {
                    myChart.hideLoading();
                    var dataset = d.info.dataset;
                    var series = []
                    for(var i=0; i<dataset.dimensions.length-1; i++) {
                        series.push({type: 'line',});
                    }
                    var option = {
                        dataset: dataset,
                        series: series,
                    }
                    console.log(option);
                    myChart.setOption(option);
                } else {
                }
            },
            error: function() {
                $(stat_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }
    get_stat();

    setInterval(function () {
        myChart.showLoading();
        get_stat();
    }, 20000);
});


