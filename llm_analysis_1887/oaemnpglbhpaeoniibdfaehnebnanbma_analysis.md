# CoCo Analysis: oaemnpglbhpaeoniibdfaehnebnanbma

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: fetch_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oaemnpglbhpaeoniibdfaehnebnanbma/opgen_generated_files/bg.js
Line 265    var responseText = 'data_from_fetch';
Line 1485   var lines = text.split(/\n/);
Line 1493   line = line.replace(/^.+content/, "");
Line 1494   line = line.replace(/\s+/g, "");
Line 1495   line = line.replace(/[='"\/>]/g, "");

**Code:**

```javascript
// bg.js - lines 1472-1509
var tgt_url = g_start_page; // g_start_page is set from chrome.tabs.query result
if(tgt_url.indexOf("?") > -1){
    tgt_url += "&" + unix_timestamp();
}
else{
    tgt_url += "?" + unix_timestamp();
}

fetch(tgt_url)
.then(function(response){
    return response.text();
})
.then(function(text){
    var lines = text.split(/\n/);
    for(var i = 0; i < lines.length; i++){
        var line = lines[i];
        if(line.indexOf("<body") > -1 || line.indexOf("<BODY") > -1){
            break;
        }

        if(line.indexOf("<meta") > -1 && line.indexOf("cxforward") > -1){
            line = line.replace(/^.+content/, "");
            line = line.replace(/\s+/g, "");
            line = line.replace(/[='"\/>]/g, "");

            var server = line;

            if(str_is_empty(server) || server.indexOf("/") > -1 || !is_valid_ip(server)){
                log.error("parse_start_page, Invalid IP!");
                return;
            }

            // Save options.
            var items = {server: server};
            chrome.storage.sync.set(items, function(){
                log.info("parse_start_page, New option saved.");
            });

            cfg.load();
            return;
        }
    }
});

// g_start_page is set from the user's current tab (line 1525):
// chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
//     g_start_page = tabs[0].url;
// });
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch source is `g_start_page`, which is the URL of the user's current tab obtained from `chrome.tabs.query()`. This is internal extension logic, not attacker-controlled data. The user's browsing to a particular page is not the same as an attacker triggering the vulnerability.

---

## Sink 2: fetch_source → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oaemnpglbhpaeoniibdfaehnebnanbma/opgen_generated_files/bg.js
Line 265    var responseText = 'data_from_fetch';
Line 1485   var lines = text.split(/\n/);
Line 1236   return "http://" + g_block_ip + "/hxlistener";
Line 1317   var tgt_url = get_hx_url() + "?action=/GBI";

**Code:**

```javascript
// bg.js - lines 1302-1318
var BLOCKIP_URL = "https://redip.nxfilter.org/redip.jsp?action=get";

function set_block_ip(){
    if(str_is_not_empty(g_block_ip)){
        log.info("set_block_ip, We already have g_block_ip = " + g_block_ip);
        return;
    }

    fetch(BLOCKIP_URL) // Hardcoded backend URL
    .then(function(response){
        return response.text();
    })
    .then(function(text){
        if(is_valid_ip(text)){
            g_block_ip = text; // Data from hardcoded backend
            log.info("set_block_ip, By remote lookup, g_block_ip = " + g_block_ip);

            var tgt_url = get_hx_url() + "?action=/GBI";
            save_block_ip(tgt_url);
        }
    });
}

function get_hx_url(){
    if(!is_valid_ip(g_block_ip)){
        log.error("get_hx_url, No g_block_ip set!");
        return "";
    }
    return "http://" + g_block_ip + "/hxlistener"; // Constructing URL to backend
}
```

**Classification:** FALSE POSITIVE

**Reason:** This flow involves hardcoded backend URLs (trusted infrastructure). The extension fetches from `BLOCKIP_URL` (hardcoded: `https://redip.nxfilter.org/redip.jsp?action=get`) to obtain an IP address, then constructs URLs to that backend server. Data from the developer's own backend is trusted infrastructure, not attacker-controlled.
