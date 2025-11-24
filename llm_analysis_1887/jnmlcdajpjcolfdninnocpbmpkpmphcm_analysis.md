# CoCo Analysis: jnmlcdajpjcolfdninnocpbmpkpmphcm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jnmlcdajpjcolfdninnocpbmpkpmphcm/opgen_generated_files/bg.js
Line 990	title: request.options.title,
Line 997	let object = {[request.options.param]: request.options.value};
Line 1001	if (request.jwt) {
Line 1005	let profile = {MNProfile: request.profile};
```

**Code:**

```javascript
// Background script - lines 986-1013
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    switch (request.type) {
        case "MN-NOTIFICATION":
            chrome.notifications.create(`mn-notification`, {
                title: request.options.title,  // ← attacker-controlled
                message: request.options.message,
                type: request.options.type,
                iconUrl: "./icons/128.png"
            })
            break;
        case "MN-SETLOCALSTORAGE":
            let object = {[request.options.param]: request.options.value};  // ← attacker-controlled
            chrome.storage.local.set(object);  // ← storage write sink
        break;
        case "MN-TOKEN":
            if (request.jwt) {
                let object = {MNJwt: request.jwt};  // ← attacker-controlled
                chrome.storage.local.set(object);  // ← storage write sink

                let profile = {MNProfile: request.profile};  // ← attacker-controlled
                chrome.storage.local.set(profile);  // ← storage write sink

                sendNotification('Поздравляю', 'Вы успешно авторизовались!');
                sendResponse({ success: true, message: 'Токен получен' });
            }
        break;
    }
});
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
    "matches": [
        "*://*.tinkoff.ru/terminal/*",
        "*://*.tbank.ru/terminal/*",
        "*://*.mindstocks.ru/*"
    ]
}
```

**Analysis:**

The extension has a `chrome.runtime.onMessageExternal` listener that accepts messages from external sources (websites matching the `externally_connectable` patterns). This listener writes attacker-controlled data directly to chrome.storage.local:

1. **Case "MN-SETLOCALSTORAGE":** Writes arbitrary key-value pairs to storage
2. **Case "MN-TOKEN":** Writes JWT tokens and profile data to storage

According to the CoCo Analysis Methodology, we IGNORE manifest.json restrictions. Even if only specific domains can trigger this, the vulnerability pattern exists.

HOWEVER, this is **storage poisoning without a retrieval path**. According to the methodology:

> **Storage poisoning alone is NOT a vulnerability:**
> - `attacker → storage.set` without retrieval = FALSE POSITIVE
> - For TRUE POSITIVE, stored data MUST flow back to attacker via:
>   - sendResponse / postMessage to attacker
>   - Used in fetch() to attacker-controlled URL
>   - Used in executeScript / eval
>   - Any path where attacker can observe/retrieve the poisoned value

The extension writes to storage but there is no code path where:
- The stored data is sent back to the attacker via sendResponse/postMessage
- The stored data is used in a subsequent vulnerable operation that benefits the attacker
- The attacker can retrieve the poisoned values

The only response is a success confirmation (`sendResponse({ success: true, message: 'Токен получен' })`) which doesn't leak the stored data back.

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While external messages can write attacker-controlled data to chrome.storage.local, there is no retrieval path for the attacker to read back the poisoned data or use it in a subsequent exploit. According to the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT a vulnerability." The stored data must flow back to the attacker through sendResponse, postMessage, or be used in attacker-accessible operations to be TRUE POSITIVE. No such path exists in this extension.
