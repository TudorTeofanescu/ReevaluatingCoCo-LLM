# CoCo Analysis: pkdmjdnphnjlhdhdambnehoacaoniloi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pkdmjdnphnjlhdhdambnehoacaoniloi/opgen_generated_files/bg.js
(No specific line numbers provided in used_time.txt - CoCo detected the flow but didn't output line details)
```

The actual extension code is minified but can be found in background.js.

**Code:**

```javascript
// Entry point - External message listener (from background.js)
chrome.runtime.onMessageExternal.addListener((function(e){
  var n=e;  // ← attacker-controlled (external message payload)
  chrome.storage.sync.set({token:n}),  // ← Storage sink
  chrome.storage.sync.get(["loginTabId","currentTabId"],(function(e){
    chrome.tabs.remove(e.loginTabId),
    chrome.storage.sync.remove("loginTabId"),
    chrome.tabs.update(e.currentTabId,{active:!0})
  }))
}))

// manifest.json shows externally_connectable:
// "externally_connectable": {
//   "matches": [
//     "*://localhost/*",
//     "*://*.peekabook.work/*"
//   ]
// }
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (localhost or *.peekabook.work)

**Attack:**

```javascript
// From a webpage on localhost or *.peekabook.work domain:
chrome.runtime.sendMessage(
  'pkdmjdnphnjlhdhdambnehoacaoniloi',  // Extension ID
  { malicious: "payload", arbitrary: "data" },  // Attacker-controlled data
  (response) => {
    console.log("Storage poisoned!");
  }
);

// The attacker's payload will be stored directly as the 'token' in chrome.storage.sync
// Example: {token: {malicious: "payload", arbitrary: "data"}}
```

**Impact:** An attacker controlling a website on localhost or the *.peekabook.work domain can send arbitrary data to the extension via chrome.runtime.sendMessage. This data is directly stored in chrome.storage.sync under the 'token' key without any validation. While the manifest.json restricts external messages to specific domains via externally_connectable, per the analysis methodology: "IGNORE manifest.json externally_connectable restrictions. If chrome.runtime.onMessageExternal exists, assume ANY attacker can exploit it. Even if only ONE domain is whitelisted, treat as TRUE POSITIVE if the flow is exploitable."

The vulnerability allows storage poisoning where an attacker can inject arbitrary data into the extension's storage. If this stored token is later used in privileged operations (fetches to backends, authentication, etc.), the attacker could potentially escalate this to further attacks. The extension has the "storage" permission in manifest.json, confirming the sink is available.

Note: While this is classified as TRUE POSITIVE due to the complete storage exploitation chain (external attacker → storage.set → potential retrieval), a full exploitation chain would require analyzing how the stored 'token' is later retrieved and used by the extension. However, the storage poisoning itself is exploitable as the attacker controls what gets written to storage from an external source.
