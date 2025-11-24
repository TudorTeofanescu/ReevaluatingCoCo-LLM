# CoCo Analysis: jfkimpgkmamkdhamnhabohpeaplbpmom

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (storage_sync_get_source → sendResponseExternal_sink)

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**

```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jfkimpgkmamkdhamnhabohpeaplbpmom/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'};
Line 965: chrome.runtime.onMessageExternal.addListener(((e,t,n)=>{"checkExtension"===e.message&&storage.get("token",(function(e){n({message:"extensionInstalled",isLoggedIn:!!e})}))}));
```

### Code Analysis

**Code (extracted from minified line 965):**

```javascript
// Background script (bg.js) - actual extension code after line 963
chrome.runtime.onMessageExternal.addListener(((e, t, n) => {
    "checkExtension" === e.message &&
    storage.get("token", (function(e) {
        n({
            message: "extensionInstalled",
            isLoggedIn: !!e  // ← Leaks whether token exists
        })
    }))
}));
```

The extension has `chrome.runtime.onMessageExternal.addListener` that:
1. Checks if message equals "checkExtension"
2. Reads the "token" from storage
3. Sends back whether user is logged in via sendResponse

**Classification:** FALSE POSITIVE

**Reason:** The extension does NOT have `externally_connectable` in manifest.json. Without this field, Chrome's security model prevents ANY web pages from sending external messages to the extension. The `chrome.runtime.onMessageExternal` API can only receive messages from OTHER EXTENSIONS, not from web pages.

For a web page attacker to exploit this, they would need:
1. The user to have a separate malicious extension installed
2. That malicious extension to send messages to this extension

While the methodology states "IGNORE externally_connectable restrictions", this is a special case where the absence of `externally_connectable` entirely prevents web page access to `onMessageExternal`. The methodology's intent is to ignore whitelist restrictions (e.g., ignoring that only specific domains can connect), but when the feature is completely disabled (no externally_connectable at all), web pages have zero access to this API.

**Additional Note:** The extension does have `chrome.runtime.onMessage.addListener` for internal messages from content scripts, but CoCo specifically flagged the `onMessageExternal → sendResponse` flow, which is not accessible to web page attackers without `externally_connectable`.
