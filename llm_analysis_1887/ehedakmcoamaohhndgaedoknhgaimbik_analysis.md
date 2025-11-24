# CoCo Analysis: ehedakmcoamaohhndgaedoknhgaimbik

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all storage.set with same fields)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehedakmcoamaohhndgaedoknhgaimbik/opgen_generated_files/bg.js
Line 968	chrome.storage.local.set({campus:request.campus, email:request.email,licenseType:request.licenseType }, () => {
```

**Code:**

```javascript
// Background script (bg.js) - Line 965-975
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.action === "setLicense") {
      chrome.storage.local.set({campus:request.campus, email:request.email,licenseType:request.licenseType }, () => {
        sendResponse({ status: "License info stored" });
        console.log("it worked")
      });
    }
    return true;  // Indicates we will send a response asynchronously
  }
);
```

**Manifest externally_connectable:**
```json
"externally_connectable": {"matches": ["https://*.teachertools-e3966.web.app/*"]}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation chain. While external websites from the whitelisted domain `*.teachertools-e3966.web.app` can trigger the `onMessageExternal` listener and poison storage with arbitrary `campus`, `email`, and `licenseType` values, there is no retrieval path back to the attacker. The stored data is never read via `storage.get` and sent back through `sendResponse`, `postMessage`, or used in any subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.). Storage poisoning alone without a retrieval mechanism is NOT exploitable per the methodology.
