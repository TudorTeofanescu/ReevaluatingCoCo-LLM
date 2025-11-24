# CoCo Analysis: onlceclhchdcgbggmfbcdefbnooahjhp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (same pattern)

---

## Sink 1: jQuery_get_source → bg_localStorage_setItem_value_sink (manifest.json)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/onlceclhchdcgbggmfbcdefbnooahjhp/opgen_generated_files/bg.js
Line 302	    var responseText = 'data_from_url_by_get';
Line 3100	var jobj = JSON.parse(data);
Line 3101	VERSION = jobj.version;
```

**Code:**
```javascript
// Background script - bg.js line 3099-3103
$.get(chrome.extension.getURL("manifest.json"), function(data) {
    var jobj = JSON.parse(data);  // ← from extension's own manifest
    VERSION = jobj.version;
    _updateURL = jobj.update_url;
    setItem("version", VERSION);  // ← localStorage sink
});
```

**Classification:** FALSE POSITIVE

**Reason:** The extension reads its own manifest.json file to extract version information. This is internal extension data, not attacker-controlled.

---

## Sink 2: jQuery_get_source → bg_localStorage_setItem_value_sink (backend API)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/onlceclhchdcgbggmfbcdefbnooahjhp/opgen_generated_files/bg.js
Line 302	    var responseText = 'data_from_url_by_get';
Line 1942	var data = response.split('|');
Line 1947	var strTicker = JSON.stringify(ticker);
```

**Code:**
```javascript
// Background script - bg.js line 1927-1953
this.requestLiveData = function() {
    var lastDataCheck = new Date().getTime();
    setItem("lastLiveDataCheck", lastDataCheck);
    var subdom = getItem("subdomain");
    var wcDomain = getItem("SubdomI");
    if (!wcDomain || wcDomain == "") {
        wcDomain = "lb";
    }
    var dataURL = "http://" + wcDomain + ".we-care.com/API/GetLiveData.php?subdom=" + subdom + "&ticker=1";
    // ← hardcoded backend domain

    $.get(dataURL, function(response) {
        if (response != '') {
            var ticker = {};
            var data = response.split('|');  // ← data from hardcoded backend
            ticker['baseRaised'] = data[0];
            ticker['type'] = data[1];
            var strTicker = JSON.stringify(ticker);
            setItem("tickerLiveData", strTicker);  // ← localStorage sink
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded backend URL (we-care.com) which is trusted infrastructure. The extension fetches live fundraising data from its own backend service and stores it locally. Compromising the backend is an infrastructure issue, not an extension vulnerability.
