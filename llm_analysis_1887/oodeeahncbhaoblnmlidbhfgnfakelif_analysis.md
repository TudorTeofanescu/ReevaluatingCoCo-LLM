# CoCo Analysis: oodeeahncbhaoblnmlidbhfgnfakelif

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_subcribeToUser → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oodeeahncbhaoblnmlidbhfgnfakelif/opgen_generated_files/cs_0.js
Line 467: window.addEventListener("subcribeToUser",function(e){chrome.runtime.sendMessage(e.detail)},!1)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oodeeahncbhaoblnmlidbhfgnfakelif/opgen_generated_files/bg.js
Line 965: s.open("GET","http://9gag.com/u/"+e.user+"/posts")

**Code:**

```javascript
// Content script (cs_0.js) - Line 467
window.addEventListener("subcribeToUser", function(e) {
    chrome.runtime.sendMessage(e.detail); // ← webpage can dispatch custom event with detail
}, !1);

// Background script (bg.js) - Line 965
chrome.runtime.onMessage.addListener(function(e, t, s) {
    if ("subcribeToUser" == e.method) {
        chrome.storage.local.get(e.user, function(t) {
            if (!t.ref) {
                var s = new XMLHttpRequest;
                s.open("GET", "http://9gag.com/u/" + e.user + "/posts"); // ← URL with attacker-controlled user
                s.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
                s.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                s.send();
                s.onload = function() {
                    if (200 === s.status) {
                        var t = {};
                        t[e.user] = {
                            ref: e.ref,
                            date: Date.now(),
                            avatar: e.avatar,
                            posts: JSON.parse(s.response).ids
                        };
                        chrome.storage.local.set(t);
                    }
                };
            }
        });
    } else {
        s({});
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows to hardcoded backend URL (trusted infrastructure). While a malicious webpage can dispatch a "subcribeToUser" event with attacker-controlled user field, the XMLHttpRequest is always sent to the hardcoded domain "http://9gag.com/u/[user]/posts". The extension is designed to interact with 9gag.com, which is the developer's trusted backend infrastructure. The attacker can only control the username parameter in the URL path, but cannot redirect requests to an arbitrary domain. Per the methodology, data flows to hardcoded backend URLs are FALSE POSITIVES as compromising the developer's own infrastructure is an infrastructure issue, not an extension vulnerability.
