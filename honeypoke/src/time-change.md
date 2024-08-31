---
theme: dashboard
---
# Change Over Time

This page shows changes to the differences in top ports connected to by percent of daily connections. Significant differences in port connections shows what ports attackers are interested over time and shifts may indicate new attacks.


```js
const time_change = FileAttachment("./data/time-change.json").json();
```

```js
//display(time_change);

var day_change_list = [];
var day_percent_list = [];

for (var i in time_change['day_differences']) {
    var current_item = time_change['day_differences'][i];
    day_change_list.push({
        "key": "today",
        "value": current_item['today_percent'],
        "port": current_item['port']
    });
    day_change_list.push({
        "key": "yesterday",
        "value": current_item['yesterday_percent'],
        "port": current_item['port']
    })
    day_percent_list.push({
        "value": current_item['percent_change']/100,
        "port": current_item['port']
    })
}

var week_change_list = [];
var week_percent_list = [];
for (var i in time_change['week_differences']) {
    var current_item = time_change['week_differences'][i];
    week_change_list.push({
        "key": "today",
        "value": current_item['today_percent'],
        "port": current_item['port']
    });
    week_change_list.push({
        "key": "week",
        "value": current_item['week_percent'],
        "port": current_item['port']
    })
    week_percent_list.push({
        "value": current_item['percent_change']/100,
        "port": current_item['port']
    })
}


```


```js
function get_percent_change({width} = {}, percent_list) {
    return Plot.plot({
        label: null,
        width,
        height: 600,
        x: {
            axis: "top",
            labelAnchor: "center",
            tickFormat: "+",
            percent: true
        },
        color: {
            scheme: "PiYG",
            type: "ordinal"
        },
        marks: [
            Plot.barX(percent_list, {
                x: "value",
                y: "port",
                fill: (d) => d.value > 0,
                sort: { y: "x" }
            }),
            Plot.gridX({ stroke: "white", strokeOpacity: 0.5 }),
            d3
            .groups(percent_list, (d) => d.value > 0)
            .map(([change, ports]) => [
                Plot.axisY({
                x: 0,
                ticks: ports.map((d) => d.port),
                tickSize: 0,
                anchor: change ? "left" : "right"
                }),
                Plot.textX(ports, {
                    x: "value",
                    y: "port",
                    text: ((f) => (d) => f(d.value))(d3.format("+.1%")),
                    textAnchor: change ? "start" : "end",
                    dx: change ? 4 : -4,
                })
            ]),
            Plot.ruleX([0])
        ]
        })
}

function get_time_change({width} = {}, change_list) {
    return Plot.plot({
        marginTop: 10,
        width,
        height: 500,
        x: {
            grid: true,
            axis: null
        },
        color: {legend: true},
        marks: [
            Plot.barY(change_list, {
                x: "key",
                y: "value",
                fill: "key",
                fx: "port",
                // sort: {x: null, color: null, fx: {value: "-y", reduce: "sum"}}
            }),
            Plot.text(change_list, {x: "key", y: "value", text: (d) => (d.value), dy: -15, 'fx': "port"}),
            Plot.ruleY([0])
        ]
    })
}

```

## Day Changes

This shows changes to the percentage ports are connected to between today and the day before. 

### Day Percent Changes
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_percent_change({width}, day_percent_list))}</div>
</div>

### Today vs. Yesterday Percentages
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_time_change({width}, day_change_list))}</div>
</div>

## Week Changes

This shows changes to the percentage ports are connected to between today and the week before. 

### Week Percent Changes
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_percent_change({width}, week_percent_list))}</div>
</div>

### Today vs. Last Week Percentages
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_time_change({width}, week_change_list))}</div>
</div>