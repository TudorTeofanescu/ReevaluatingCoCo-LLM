# CoCo Analysis: geceheceigppknljieeenfghnlmoiobp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/geceheceigppknljieeenfghnlmoiobp/opgen_generated_files/bg.js
Line 972: `opend = request.getSelectedContent;`

**Code:**

```javascript
// Background script - Message handler (bg.js)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    console.info("------------------------------- Got request", request);

    opend = request.getSelectedContent; // Line 972 - attacker-controlled

    if (request.getSelectedContent) {
      chrome.tabs.getSelected(null, function(tab) {
        tableCalleMe = tab.id;
      });

      chrome.storage.local.set({'camera': request.getSelectedContent}, function() {
        selectedContent = 'Value is set to ' + request.getSelectedContent;
      });
      sendResponse(selectedContent);

    } else {
      chrome.storage.local.set({'camera': request.getSelectedContent}, function() {
        console.log('Value is set to ' + request.getSelectedContent);
      });
      tableCalleMe = -1;
    }
  });
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While attacker-controlled data from `chrome.runtime.onMessageExternal` flows to `chrome.storage.local.set()`, there is no retrieval path where the attacker can read back the poisoned data. The stored value is never sent back to the attacker via `sendResponse`, `postMessage`, or used in any subsequent vulnerable operation that would benefit the attacker. According to the methodology, storage poisoning alone without a retrieval mechanism is NOT exploitable and classified as a FALSE POSITIVE.
