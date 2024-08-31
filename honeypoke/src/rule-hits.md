---
theme: dashboard
---
# Exploit Hits

```js
const rules_hit = FileAttachment("./data/hits.json").json();
```

```js
// display(rules_hit);

var remote_ip_data = rules_hit['remote_ip_data'];


var new_array = [];
for (var key in rules_hit['rules']) {
    new_array.push({
        "rule_name": key,
        "value": rules_hit['rules'][key]
    })
}

var remote_ip_tree = [];
var port_tree = [];
var port_tree_map = {};
var country_map = {};
for (var remote_ip in rules_hit['remote_ips']) {
    for (var port_data in rules_hit['remote_ips'][remote_ip]) {
        for (var rule_name in rules_hit['remote_ips'][remote_ip][port_data]) {
            var country = remote_ip_data[remote_ip]['country'];

            remote_ip_tree.push({
                "name": country + "!" + remote_ip + "!" + port_data + "!" + rule_name + ": " + rules_hit['remote_ips'][remote_ip][port_data][rule_name]
            })

            var port_path = port_data + "!" + rule_name;
            if (!(port_path in port_tree_map)) {
                port_tree_map[port_path] = 0;
            }
            port_tree_map[port_path] += rules_hit['remote_ips'][remote_ip][port_data][rule_name];

            var country = rules_hit['remote_ip_data'][remote_ip]['country'];
            if (!(country in country_map)) {
                country_map[country] = {};
            }
            if (!(rule_name in country_map[country])) {
                country_map[country][rule_name] = 0;
            }
            country_map[country][rule_name] += rules_hit['remote_ips'][remote_ip][port_data][rule_name];
        }
    }
}


for (var port_path in port_tree_map) {
    port_tree.push({
        "name": port_path + ": " + port_tree_map[port_path]
    })
}


var country_tree = [];
for (var country in country_map) {
    for (var rule_name in country_map[country]) {
        country_tree.push({
            "name": country + "!" + rule_name + ": " + country_map[country][rule_name]
        })
    }
}
```

```js
function get_rule_hit({width} = {}) {
    return Plot.plot({
        marginLeft: 600,
        width,
        height: 500,
        x: {
            axis: "top",
            grid: true,
        },
        marks: [
            // Plot.ruleX([0]),
            Plot.barX(new_array, {x: "value", y: "rule_name", sort: {y: "x", reverse: true}}),
            Plot.text(new_array, {x: "value", y: "rule_name", text: (d) => (d.value), dx: 15}),
        ]
    })
}
```

## Rule Hit Totals
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_rule_hit({width}))}</div>
</div>

```js
function get_remote_ip_data({width} = {}) {

    var height = remote_ip_tree.length * 25;

    return Plot.plot({
        axis: null,
        margin: 10,
        marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(remote_ip_tree, {path: "name", delimiter: "!"})
        ]
    })
}
```

## Hits by Remote IP

<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_remote_ip_data({width}))}</div>
</div>


```js
function get_port_data({width} = {}) {

    var height = port_tree.length * 25;

    return Plot.plot({
        axis: null,
        margin: 10,
        // marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(port_tree, {path: "name", delimiter: "!"})
        ]
    })
}
```

## Hits by Ports

<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_port_data({width}))}</div>
</div>

```js
function get_country_data({width} = {}) {

    var height = country_tree.length * 25;

    return Plot.plot({
        axis: null,
        margin: 10,
        // marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(country_tree, {path: "name", delimiter: "!"})
        ]
    })
}
```

## Hits by Country

<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_country_data({width}))}</div>
</div>