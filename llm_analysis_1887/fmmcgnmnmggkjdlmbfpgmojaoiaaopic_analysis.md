# CoCo Analysis: fmmcgnmnmggkjdlmbfpgmojaoiaaopic

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fmmcgnmnmggkjdlmbfpgmojaoiaaopic/opgen_generated_files/cs_1.js
Line 467: Content script with window.addEventListener("message") that flows to chrome.storage.local.set()

**Code:**

```javascript
// Content script (cs_1.js, line 467) - Entry point
window.addEventListener("message",(async S=>{
    const _=S.data; // ← attacker-controlled via postMessage
    switch(_.type){
        case"DOCAI_SET_AUTH":{
            const E=_.payload; // ← attacker-controlled payload
            // Storage write sink - attacker controls the auth token
            if(chrome.storage.local.set({[R.auth]:E}),!E)
                return void chrome.storage.local.set({[R.isAuthenticated]:!1});
            chrome.storage.local.set({[R.isAuthenticated]:!0});
            break
        }
        case"DOCAI_SHOW_POPUP":
            chrome.runtime.sendMessage({type:E.REQUEST_SHOW_POPUP})
    }
}))
```

**Manifest Permissions:**
- `storage` permission: ✓ Present

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On any webpage where the extension's content script runs (all URLs per manifest)
window.postMessage({
    type: "DOCAI_SET_AUTH",
    payload: "attacker-controlled-fake-token"
}, "*");

// This poisons the extension's storage with a fake authentication token
// The attacker can set arbitrary values for:
// - storage.auth (authentication token)
// - storage.isAuthenticated (authentication status)
```

**Impact:** Storage poisoning vulnerability. An attacker on any webpage can inject malicious authentication tokens into the extension's storage, potentially bypassing authentication checks or setting fake credentials that the extension will use in subsequent operations.
