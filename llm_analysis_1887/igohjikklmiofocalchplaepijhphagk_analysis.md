# CoCo Analysis: igohjikklmiofocalchplaepijhphagk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 5 (storage.local.set for fratol_ip, fratol_port, fratol_login, fratol_pass - multiple flows)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/igohjikklmiofocalchplaepijhphagk/opgen_generated_files/cs_0.js
Line 467: `window.addEventListener('message', function (e) {`
Line 471: `if (e.data.type && e.data.type == 'a.e.') {`
Line 472: `send('a.e.', e.data.d);`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/igohjikklmiofocalchplaepijhphagk/opgen_generated_files/bg.js
Line 973: `var data = JSON.parse(request.d);`
Line 974-978: Multiple `chrome.storage.local.set` calls with data.ip, data.port, data.login, data.pass

**Code:**

```javascript
// Content script - cs_0.js (Line 467-480)
window.addEventListener('message', function (e) {
    if (e.source != window) {
        return;
    }
    if (e.data.type && e.data.type == 'a.e.') {
        send('a.e.', e.data.d); // ← attacker-controlled via postMessage
    }
    // ...
}, false);

function send(t, d) {
    chrome.runtime.sendMessage({t: t, d: d}, function (r) {
    });
}

// Background script - bg.js (Line 970-992)
chrome.runtime.onMessage.addListener(function (request, sender, response) {
    if (request.t && request.t == 'a.e.') {
        if (request.d) {
            var data = JSON.parse(request.d); // ← attacker-controlled data
            if (data.request.data){
                data = data.request.data;
                chrome.storage.local.set({fratol_ip: data.ip}); // Storage write
                chrome.storage.local.set({fratol_port: data.port}); // Storage write
                chrome.storage.local.set({fratol_login: data.login}); // Storage write
                chrome.storage.local.set({fratol_pass: data.pass }).then(function(){ // Storage write
                    response({status: 'got'});
                    task(request.t, request.d);
                });
            }
        }
    }
    // ...
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation - storage poisoning only. The attacker can write data to storage (fratol_ip, fratol_port, fratol_login, fratol_pass) via window.postMessage, but there is no retrieval path where the poisoned data flows back to the attacker through sendResponse, postMessage, or to an attacker-controlled URL. The stored values are used internally by the extension (passed to the `task()` function), but the attacker cannot retrieve or observe these poisoned values. According to the methodology, storage poisoning alone without a retrieval path is NOT exploitable.

---
