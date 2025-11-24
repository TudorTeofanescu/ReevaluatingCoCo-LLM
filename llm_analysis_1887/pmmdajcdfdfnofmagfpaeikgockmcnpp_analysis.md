# CoCo Analysis: pmmdajcdfdfnofmagfpaeikgockmcnpp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pmmdajcdfdfnofmagfpaeikgockmcnpp/opgen_generated_files/bg.js
Line 1218	chrome.storage.local.set({ authToken: message.payload }, function () {
	message.payload
```

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin !== MEMENTO_WEB_URL) {
      return;
    }
    if (message.type == MESSAGE_TYPE_SET_AUTH_TOKEN) {
      chrome.storage.local.remove(CSRF_TOKEN_STORAGE_KEY);
      chrome.storage.local.set({ authToken: message.payload }, function () { // ← stores external data
        console.log("Auth token saved to storage = " + message.payload);
      });
    }
  }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While external websites can send messages and poison the authToken in storage, this is incomplete storage exploitation. The stored authToken is only used to authenticate with the developer's hardcoded backend (MEMENTO_WEB_URL). There is no retrieval path that sends the poisoned data back to the attacker. The stored token flows to trusted infrastructure (developer's backend servers), which per methodology rules is not a vulnerability.
