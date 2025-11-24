# CoCo Analysis: ellfmoopomppmhljhjkbmninmnkoebfn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_sendUserInfoEvent → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ellfmoopomppmhljhjkbmninmnkoebfn/opgen_generated_files/cs_0.js
Line 467 (minified extension code after third "// original" marker)
Flow: document.addEventListener("sendUserInfoEvent") → e.detail.message → chrome.storage.local.set
```

**Code:**
```javascript
// Content script (cs_0.js line 467, formatted for clarity)

// Entry point - custom DOM event listener
document.addEventListener("sendUserInfoEvent", e => { // ← attacker can dispatch this event
    console.log("event.detail:", e.detail.message);
    const t = JSON.parse(e.detail.message); // ← attacker-controlled data

    // Storage write sink
    chrome.storage.local.set({
        accessToken: t.accessToken, // ← attacker-controlled
        user: t.user // ← attacker-controlled
    }, () => {
        console.log("Data stored in chrome.storage");
    });
});

// Separate handler (not related to storage retrieval)
chrome.runtime.onMessage.addListener((e, t, n) => {
    if ("getContent" === e.action) {
        n({content: document.body.innerHTML}); // Returns HTML, not storage data
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While an attacker can poison chrome.storage.local by dispatching a custom "sendUserInfoEvent" with malicious accessToken and user data, there is no retrieval path for the attacker to observe or retrieve the stored data. Per the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable. The attacker MUST be able to retrieve the poisoned data back via sendResponse, postMessage, or triggering a read operation that sends data to attacker-controlled destination." The message listener that returns document.body.innerHTML is unrelated to storage and does not provide a way to exfiltrate the stored data. This is a FALSE POSITIVE pattern: "attacker → storage.set only (no retrieval path to attacker)".
