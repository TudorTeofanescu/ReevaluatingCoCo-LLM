# CoCo Analysis: apndpbnhnhpddgndohglpofednmlfnkj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (2x chrome_storage_sync_set_sink, 1x chrome_storage_local_set_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apndpbnhnhpddgndohglpofednmlfnkj/opgen_generated_files/bg.js
Line 1034: `if(request.header && !request.body) {`
Line 1035: `chrome.storage.sync.set({ "ffb_language": request.header }, function(){});`

**Code:**

```javascript
// Background script - bg.js (lines 1022-1040)
chrome.runtime.onMessageExternal.addListener(
  async (request, sender, sendResponse) => {
    if (request.url) {
      if (request.handleCors) {
        var res = await fetcore(
          request.url,
          request.method,
          request.header,  // ← attacker-controlled
          request.body     // ← attacker-controlled
        );
        sendResponse(res);
      } else {
        if(request.header && !request.body) {
          // Storage poisoning
          chrome.storage.sync.set({ "ffb_language": request.header }, function(){});
          sendResponse('{ "success": "true" }');
        } else if(!request.method && request.header && request.body) {
          // Storage poisoning
          chrome.storage.sync.set({ "script_param": request.body }, function(){});
          chrome.storage.local.set({ "exchange_rates": request.header }, function(){});
          sendResponse('{ "success": "true" }');
        }
      }
    }
  }
);

// Content script retrieves data (cs_0.js, line 467)
chrome.storage.sync.get(["script_param"], function(n) {
  // Data used internally for UI configuration
  // Sent to hardcoded Facebook/graph.facebook.com URLs
});

chrome.storage.sync.get(["ffb_language"], function(e) {
  // Data used internally for language localization
  // Not sent back to attacker
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation chain. While the extension accepts external messages from any website (due to `externally_connectable: ["http://*/*", "https://*/*"]`) and stores attacker-controlled data, the poisoned data is only retrieved for internal use in the content script. The retrieved values are used for UI configuration and sent to hardcoded trusted infrastructure (graph.facebook.com, business.facebook.com, adsmanager.facebook.com). There is no retrieval path where the attacker can observe or retrieve the poisoned data back via sendResponse, postMessage, or any attacker-accessible output. Per the methodology, storage poisoning alone without a retrieval path to the attacker is NOT a vulnerability.

---

## Sink 2 & 3: Same flow as Sink 1

The other two sinks (`request.body` → chrome_storage_sync_set_sink and `request.header` → chrome_storage_local_set_sink) follow the same pattern - storage poisoning without exploitable retrieval path. All retrieved storage data flows to hardcoded Facebook/FFB infrastructure, not back to the attacker.
