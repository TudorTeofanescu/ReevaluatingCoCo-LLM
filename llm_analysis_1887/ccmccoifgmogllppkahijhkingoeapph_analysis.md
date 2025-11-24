# CoCo Analysis: ccmccoifgmogllppkahijhkingoeapph

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: XMLHttpRequest_responseText_source → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccmccoifgmogllppkahijhkingoeapph/opgen_generated_files/bg.js
Line 332 XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 965 var allextensionsinfo={},disableactiveextensions=!1,disabledactiveextensions=[],currenttoken=localStorage.getItem("token"),favouritesarray=localStorage.getItem("favourites")...
Line 965 ...JSON.parse(e.responseText)...
Line 965 ...a.token...

**Code:**

```javascript
// Background script (bg.js)
var backgroundloaded = function() {
    sendData(null === currenttoken ? "newtoken" : "ready");
    // ... rest of initialization
};

var sendData = function(a, b, c) {
    var d = "https://www.manycontacts.com/api/sargent/"; // Hardcoded backend URL
    "kiloglamfncknhooihikpjdnacleboif" == chrome.runtime.id && (d = "http://manycontacts.vm/api/sargent/");

    "newtoken" == a ?
        sendPOST(d, {token: "", version: version}, function(a) {
            "undefined" != typeof a.token && (
                currenttoken = a.token, // Data from hardcoded backend
                localStorage.setItem("token", currenttoken) // Store backend response
            )
        }) :
        "ready" == a ? sendPOST(d, {token: currenttoken, version: version}, c) :
        "checker" == a && sendPOST(d, b, c)
};

var sendPOST = function(a, b, c) {
    var d = JSON.stringify(b),
        e = new XMLHttpRequest;
    e.open("POST", a, !0); // POST to hardcoded URL
    e.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    e.onload = function() {
        var a = JSON.parse(e.responseText); // Response from hardcoded backend
        4 == e.readyState && "200" == e.status && "function" == typeof c && c(a)
    };
    e.send(encodeURI(d));
};

// Only listens to internal messages, not external
chrome.runtime.onMessage.addListener(function(a, b, c) {
    if ("reloadPolice" == a.options) chrome.runtime.reload(), c({answer: "ok"});
    // ... rest of message handling
});

backgroundloaded();
```

**Classification:** FALSE POSITIVE

**Reason:** Data comes from hardcoded backend URL (https://www.manycontacts.com/api/sargent/), which is trusted infrastructure. The flow is: hardcoded backend URL → XMLHttpRequest response → localStorage. There is no external attacker trigger (only chrome.runtime.onMessage, not onMessageExternal). Compromising the developer's backend server is a separate infrastructure issue, not an extension vulnerability. This is trusted data from the extension's own backend being stored locally.
