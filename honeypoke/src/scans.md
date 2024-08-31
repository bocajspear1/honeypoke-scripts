---
theme: dashboard
---
# Scans

```js
const scans = FileAttachment("./data/scans.json").json();
```

```js
//display(scans);

var seek_and_attack = [];
var seen_attack_seeks = [];
var seek_and_scan = [];
var seen_scan_seeks = [];

var remote_ip_data = scans['remote_ip_data'];

var wide_scan_tree = [];
for (var i in scans['scans']['wide_scans']) {
    var result_item = scans['scans']['wide_scans'][i];

    var port = result_item[1];
    var country = remote_ip_data[result_item[0]]['country'];
    var ip_addr = result_item[0];

    wide_scan_tree.push({
        "name": country + "!" + ip_addr + "!" + port + ": " + result_item[2].length
    })


    // Loop through brute forces to find items scanning and then attacking
    for (var j in scans['scans']['brute_forces']) {
        var brute_force_item = scans['scans']['brute_forces'][j];
        var seek_path = brute_force_item[0] + "!" + result_item[1];

        if (brute_force_item[0] == result_item[0] && seen_attack_seeks.indexOf(seek_path) == -1) {
            
            seek_and_attack.push({
                "Remote IP": result_item[0],
                "Port": result_item[1],
                "Country": country
            })
            seen_attack_seeks.push(seek_path)
        }
    }

    // Loop through tall scan to find attackers scanning one then many more
    for (var j in scans['scans']['tall_scans']) {
        var tall_scan_item = scans['scans']['tall_scans'][j];
        var seek_path = tall_scan_item[0] + "!" + result_item[1];

        if (tall_scan_item[0] == result_item[0] && seen_scan_seeks.indexOf(seek_path) == -1) {

            var other_ports = 
            
            seek_and_scan.push({
                "Remote IP": result_item[0],
                "Country": country,
                "Port Scanned": port,
                "Number of Other Ports": tall_scan_item[1].length
            })
            seen_scan_seeks.push(seek_path)
        }
    }
}


function get_wide_scans({width} = {}) {
    var height = wide_scan_tree.length * 25;

    return Plot.plot({
        axis: null,
        margin: 10,
        marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(wide_scan_tree, {path: "name", delimiter: "!"})
        ]
    })
}

```

## Wide Scans by Remote IP

Wide scans are scans detected across multiple systems within a certain time of each other, likely indicating an attacker scanned a certain port across the internet or wide range of addresses.

<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_wide_scans({width}))}</div>
</div>

## Remote IPs Scan and Attack

These addresses performed a wide scan then started to brute force/perform attacks against the port.

```js
display(Inputs.table(seek_and_attack, {
    "multiple": false
}));
```

## Remote IPs Scan and Investigate

These addresses performed a wide scan then scanned the system more heavily.

```js
display(Inputs.table(seek_and_scan));
```


```js

var tall_scan_tree = [];
for (var i in scans['scans']['tall_scans']) {
    var result_item = scans['scans']['tall_scans'][i];
    var country = remote_ip_data[result_item[0]]['country'];
    for (var j in result_item[1]) {
        tall_scan_tree.push({
            "name": country + "!" + result_item[0] + "!" + result_item[1][j]
        })
    }
    
    
}

function get_tall_scans({width} = {}) {
    var height = tall_scan_tree.length * 25;

    return Plot.plot({
        axis: null,
        margin: 10,
        marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(tall_scan_tree, {path: "name", delimiter: "!"})
        ]
    })
}
```

## Tall Scans by Remote IP
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_tall_scans({width}))}</div>
</div>



```js
var brute_force_tree = [];
var brute_force_port_map = {};
for (var i in scans['scans']['brute_forces']) {
    var result_item = scans['scans']['brute_forces'][i];
    var port = result_item[1];
    var country = remote_ip_data[result_item[0]]['country'];

    brute_force_tree.push({
        "name": country + "!" + result_item[0] + "!" + port + "!" + result_item[2] + ": " + result_item[3]
    })

    if (!(port in brute_force_port_map)) {
        brute_force_port_map[port] = 0;
    }
    brute_force_port_map[port] += result_item[3];
}


var brute_force_list = [];
for (var port in brute_force_port_map) {
    brute_force_list.push({
        "port": port,
        "count": brute_force_port_map[port]
    })
}

function get_brute_forces({width} = {}) {
    var height = brute_force_tree.length * 30;

    return Plot.plot({
        axis: null,
        margin: 10,
        marginLeft: 40,
        // marginRight: 160,
        // width: width,
        height: height,
        marks: [
            Plot.tree(brute_force_tree, {path: "name", delimiter: "!"})
        ]
    })
}
```

## Brute Force Attacks by Remote IP
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_brute_forces({width}))}</div>
</div>

```js
function get_brute_force_ports({width} = {}) {
    return Plot.plot({
        marginLeft: 100,
        marginRight: 100,
        width,
        height: 500,
        x: {
            axis: "top",
            grid: true,
        },
        marks: [
            // Plot.ruleX([0]),
            Plot.barX(brute_force_list, {x: "count", y: "port", sort: {y: "x", reverse: true}}),
            Plot.text(brute_force_list, {x: "count", y: "port", text: (d) => (d.count), dx: 17}),
        ]
    })
}
```

## Brute Force Attacks by Port
<div class="grid grid-cols-1">
  <div class="card">${resize((width) => get_brute_force_ports({width}))}</div>
</div>
