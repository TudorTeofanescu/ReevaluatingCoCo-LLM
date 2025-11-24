# CoCo Analysis: eeedhncneejmgokflckdfjagaidichbb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eeedhncneejmgokflckdfjagaidichbb/opgen_generated_files/bg.js
Line 998: `chrome.storage.local.set({ jwt: message.token }, function() {`

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
  console.log('Received external message:', message);
  if (message && message.type === 'SEND_JWT') {
    chrome.storage.local.set({ jwt: message.token }, function() { // ← Attacker can poison storage
      if (chrome.runtime.lastError) {
        console.error('Error setting JWT token in storage:', chrome.runtime.lastError);
        sendResponse({ success: false });
      } else {
        console.log('JWT token stored in chrome.storage.local.');
        sendResponse({ success: true });
      }
    });
    return true;
  }
});

// Internal message handler (NOT accessible to external attackers)
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  console.log('Received message:', message);
  if (message && message.type === 'GET_TOKEN') {
    chrome.storage.local.get('jwt', function(data) {
      sendResponse({ token: data.jwt }); // ← Only internal scripts can retrieve
    });
    return true;
  }
});

// manifest.json externally_connectable:
// "externally_connectable": {
//   "matches": ["https://app.praktiker.se/*"]
// }
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While an external attacker (from https://app.praktiker.se/*) can poison the storage by sending a SEND_JWT message via chrome.runtime.onMessageExternal, there is no path for the attacker to retrieve the poisoned data. The GET_TOKEN handler that reads from storage is only available via chrome.runtime.onMessage (internal messages), not onMessageExternal. Storage poisoning alone without a retrieval path is not exploitable according to the methodology - the attacker must be able to retrieve the poisoned value back through sendResponse, postMessage, or use it in a subsequent vulnerable operation.
