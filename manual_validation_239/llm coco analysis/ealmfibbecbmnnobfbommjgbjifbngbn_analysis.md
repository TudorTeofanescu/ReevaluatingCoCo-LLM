# CoCo Analysis: ealmfibbecbmnnobfbommjgbjifbngbn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ealmfibbecbmnnobfbommjgbjifbngbn/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 1061: var mdats = JSON.parse(jsdata);
Line 1063: chrome.browserAction.setIcon({path: mdats.FileName+'.png'});
Line 1065: chrome.storage.local.set({iconsname: mdats.FileName});

**Code:**

```javascript
// Background script - chrome.tabs.onActivated listener (lines 1036-1077)
chrome.tabs.onActivated.addListener(function(activeInfo) {
  chrome.tabs.get(activeInfo.tabId, function(tab){
    var tabURL = extractHostname(tab.url);
    chrome.storage.local.set({urlsf: tabURL});

    var urls = "https://www.fascores.com/api/FAScores/Get_Scores"; // Hardcoded backend URL
    var xhr = new XMLHttpRequest();
    xhr.open("POST", urls);
    xhr.setRequestHeader("Authorization", "Basic REVWVXNlcjIyOkZBUyEwMjIyUFdEMjE=");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.responseText !== "null") {
          var jsdata = xhr.responseText; // Data from developer's backend
          var mdats = JSON.parse(jsdata);
          chrome.browserAction.setIcon({path: mdats.FileName+'.png'});
          chrome.storage.local.set({iconsname: mdats.FileName}); // Storage sink
        }
      }
    };

    var data = '{"URL":"'+extractHostname(tabURL)+'"}';
    xhr.send(data);
  });
});
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded developer backend URL (`https://www.fascores.com/api/FAScores/Get_Scores`) to storage. This is trusted infrastructure - the developer trusts their own backend server. No attacker-controlled data flows to storage.

---

## Sink 2: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ealmfibbecbmnnobfbommjgbjifbngbn/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 1102: var mdats = JSON.parse(jsdata);
Line 1104: chrome.browserAction.setIcon({path: mdats.FileName+'.png'});
Line 1106: chrome.storage.local.set({iconsname: mdats.FileName});

**Code:**

```javascript
// Background script - setTimeout/chrome.tabs.query (lines 1080-1123)
setTimeout(function(){
  chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    let url = tabs[0].url;
    chrome.storage.local.set({urlsf: extractHostname(url)});

    var urls = "https://www.fascores.com/api/FAScores/Get_Scores"; // Hardcoded backend URL
    var xhr = new XMLHttpRequest();
    xhr.open("POST", urls);
    xhr.setRequestHeader("Authorization", "Basic REVWVXNlcjIyOkZBUyEwMjIyUFdEMjE=");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.responseText !== "null") {
          var jsdata = xhr.responseText; // Data from developer's backend
          var mdats = JSON.parse(jsdata);
          chrome.browserAction.setIcon({path: mdats.FileName+'.png'});
          chrome.storage.local.set({iconsname: mdats.FileName}); // Storage sink
        }
      }
    };

    var data = '{"URL":"'+extractHostname(url)+'"}';
    xhr.send(data);
  });
}, 1000);
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded developer backend URL (`https://www.fascores.com/api/FAScores/Get_Scores`) to storage. This is trusted infrastructure - the developer trusts their own backend server. No attacker-controlled data flows to storage.
