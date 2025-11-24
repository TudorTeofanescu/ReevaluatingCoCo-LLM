# CoCo Analysis: ochddbabahkpldnmkhpjggapdpmcdpig

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6 (all variations of the same flow)

---

## Sink 1-6: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ochddbabahkpldnmkhpjggapdpmcdpig/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 1063: time = parseInt(page.match(/var left = parseInt\([0-9]+/g)[0].match(/[0-9]+/)[0])
Line 1039: time = parseInt(page.match(/var left = parseInt\([0-9]+/g)[0].match(/[0-9]+/)[0])

**Code:**

```javascript
// Background script - parse function (line 1010-1120)
var parse = function(key, site) {
    getStorage(site, function(base){
        if (base[site][key] == undefined || base[site][key] == null || base[site][key]['time'] == 'end' || freezeTime[site] > new Date().getTime()){
            return;
        }
        var xhr = new XMLHttpRequest();
        if(site == 'anidub'){
            api_key = 'https://mycoub.ru/api-grabbing?url=' + key
            xhr.open('GET', api_key, true);
        } else {
            xhr.open('GET', key, true); // Fetching from anime tracking sites
        }
        xhr.send();
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    var page = xhr.responseText; // Response from anime sites
                    switch(site){
                        case 'anistar':
                            // Parse episode information from HTML
                            time = parseInt(page.match(/var left = parseInt\([0-9]+/g)[0].match(/[0-9]+/)[0])
                            // ...
                            break
                        case 'animevost':
                            // Similar parsing
                            break
                        // Other anime sites...
                    }
                    // Store parsed episode data
                    setStorage(key, lastEpisodeNum, site, time);
                }
            }
        };
    });
}

// Storage function (line 1175-1182)
var setStorage = function(url, num, site, time){
    getStorage(site, function(base){
        if(num != null)
            base[site][url]['epizodes'] = num; // Store episode number
        base[site][url]['time'] = time; // Store time
        chrome.storage.local.set(base); // Storage sink
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from anime tracking websites (anistar.org, animevost.org, anilibria.org, anidub.org) to storage. These are the websites the extension is designed to monitor for new anime episodes. This is trusted infrastructure - the extension fetches data from its intended backend services to track anime releases. Compromising these anime websites would be an infrastructure issue, not an extension vulnerability.
