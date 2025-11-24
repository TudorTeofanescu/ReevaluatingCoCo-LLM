# CoCo Analysis: ocdaddnoglnhhebjlcphhophmohdoocj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all variations of the same storage poisoning flow)

---

## Sink 1-4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ocdaddnoglnhhebjlcphhophmohdoocj/opgen_generated_files/bg.js
Line 977: if (request.tiktokOpenId && request.tiktokUserName && request.tiktokAvatarUrl)

**Code:**

```javascript
// Background script - background.js (line 975-987)
chrome.runtime.onMessageExternal.addListener(
    function(request, _sender, _sendResponse) {
        if (request.tiktokOpenId && request.tiktokUserName && request.tiktokAvatarUrl) {
            saveSession(request) // Attacker-controlled data stored
        }
    }
);

function saveSession(sessionPayload) {
    chrome.storage.local.set({userProfile: sessionPayload}, function() {
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. The attacker can poison storage with arbitrary data via chrome.runtime.onMessageExternal, but there is no mechanism for the attacker to retrieve this data back (no sendResponse, no storage.get that returns data to attacker). Storage poisoning alone is not exploitable.
