# CoCo Analysis: hiplomkbpcjkecngbffdbgcikeajpied

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hiplomkbpcjkecngbffdbgcikeajpied/opgen_generated_files/bg.js
Line 991: chrome.tabs.sendMessage(tabs[0].id, { message: "from_web", data: req.data });

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hiplomkbpcjkecngbffdbgcikeajpied/opgen_generated_files/cs_0.js
Line 641: if (req.data.appId)

**Code:**

```javascript
// background.js - External message handler (lines 987-995)
chrome.runtime.onMessageExternal.addListener(function (req, sender, sendResponse) {
    console.log("Background receiving req", req);
    if (req) {
        chrome.tabs.query({ active: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, { message: "from_web", data: req.data });  // <- forwards to content script
        });
        return true;
    };
});

// content-script.js - Message handler (lines 640-649)
case "from_web":
    if (req.data.appId) {
        chrome.storage.sync.set({appId: req.data.appId});  // <- storage write sink, never retrieved
    } else {
        insertMoonback(
            (req.data.html) ? true : false,
            req.data.html ? req.data.html : req.data.text,
            mb_editableContainer
        );
    }
break;
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation - the extension writes attacker-controlled `req.data.appId` to `chrome.storage.sync.set()` but never retrieves this value. Grep search of the entire codebase shows no `storage.sync.get` operations that read the 'appId' key. Per the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable!" The stored value must flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation to be TRUE POSITIVE. While the extension also has `insertMoonback()` functionality that processes `req.data.html` and `req.data.text`, CoCo specifically flagged the storage.sync.set sink, which lacks a retrieval path.
