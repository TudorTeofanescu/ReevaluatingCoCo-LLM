# CoCo Analysis: ejndbonkbfpfgaghpgknmljhafpkkjik

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_auth → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ejndbonkbfpfgaghpgknmljhafpkkjik/opgen_generated_files/cs_0.js
Line 565: document.addEventListener("auth", function(data) {
Line 566: var message = data.detail;
Line 567: chrome.runtime.sendMessage({ type: message.type, access_token: (message.access_token ? message.access_token : undefined) });

**Code:**

```javascript
// Content script (cs_0.js) - Lines 565-568
// DOM event listener - Entry point
document.addEventListener("auth", function(data) {
    var message = data.detail; // ← attacker-controlled from webpage
    chrome.runtime.sendMessage({
        type: message.type, // ← attacker-controlled
        access_token: (message.access_token ? message.access_token : undefined) // ← attacker-controlled
    });
});

// Background script (bg.js) - Lines 997-1003
// Message handler - Sink
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type === 'loggedIn') {
        // Stores attacker-controlled access_token in localStorage
        localStorage.setItem('markbook_access_token', request.access_token); // ← sink
    } else if (request.type === 'loggedOut') {
        localStorage.removeItem('markbook_access_token');
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// From any webpage (extension content script runs on http://*/* and https://*/*)
// Attacker creates and dispatches a custom "auth" event
var maliciousEvent = new CustomEvent("auth", {
    detail: {
        type: "loggedIn",
        access_token: "attacker_controlled_token_12345"
    }
});
document.dispatchEvent(maliciousEvent);

// The content script will receive this event and forward it to the background script
// The background script will then store the attacker-controlled token in localStorage
```

**Impact:** Any webpage can dispatch a custom "auth" event to poison the extension's localStorage with an arbitrary access_token. This allows an attacker to:
1. Replace the legitimate user's access token with a malicious one
2. Cause the extension to use an attacker-controlled token for authentication
3. Potentially hijack the user's Markbook account or cause authentication failures
4. The stored token is likely used for API authentication in subsequent extension operations

**Note:** Per the methodology, this is classified as TRUE POSITIVE because:
1. External attacker can trigger the flow via DOM event (document.addEventListener)
2. Content script matches all URLs ("http://*/*", "https://*/*") per manifest.json, but per CRITICAL RULE #1, we ignore manifest restrictions
3. Attacker controls the data flowing to the sink (message.access_token)
4. The flow achieves storage poisoning with a security-critical value (authentication token)
5. Per CRITICAL RULE #1: "If code has document.addEventListener(), assume ANY attacker can trigger it"
