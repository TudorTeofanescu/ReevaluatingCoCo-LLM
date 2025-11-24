# CoCo Analysis: kpnbecjflplljegmbglojdlgbmjgkiei

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kpnbecjflplljegmbglojdlgbmjgkiei/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessageExternal.addListener receiving external message
Line 965 - e.payload extracted from external message
Line 965 - chrome.storage.sync.set storing attacker data

**Code:**

```javascript
// Background script - bg.js (original extension code after line 963, minified webpack bundle)
// Decompiled/formatted relevant portion:

chrome.runtime.onMessageExternal.addListener((function(e) {
    var t = e.type,
        n = e.payload,
        r = void 0 === n ? {} : n;

    if (t === a.ON_SIGN_IN) { // a.ON_SIGN_IN = "ON_SIGN_IN"
        var o = {},
            i = r.profile,   // ← attacker-controlled
            u = r.keys,       // ← attacker-controlled
            f = r.userId;     // ← attacker-controlled

        // Store profile data
        i && Object.keys(i).length && (
            o[c.PROFILE] = i,
            i.plan && (o[c.PLAN] = i.plan),
            i.freeTrialExpirationDate && (o[c.FREE_TRIAL_EXPIRATION_DATE] = i.freeTrialExpirationDate)
        ),

        // Store keys data
        u && Object.keys(u).length && (o[c.KEYS] = u),

        // Store userId
        f && (o[c.USER_ID] = f),

        // Write to storage
        chrome.storage.sync.set(o) // ← Storage write sink
    }
}))

// Constants from the webpack bundle:
// c.PROFILE = "PROFILE"
// c.PLAN = "PLAN"
// c.FREE_TRIAL_EXPIRATION_DATE = "FREE_TRIAL_EXPIRATION_DATE"
// c.KEYS = "KEYS"
// c.USER_ID = "USER_ID"
// a.ON_SIGN_IN = "ON_SIGN_IN"
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While the extension has chrome.runtime.onMessageExternal listener that stores attacker-controlled data (profile, keys, userId) from external messages into chrome.storage.sync, there is no retrieval path that sends the stored data back to the attacker.

For this to be a TRUE POSITIVE, the stored data would need to:
1. Be retrieved via chrome.storage.sync.get, AND
2. Sent back to the attacker via sendResponse, postMessage, or used in a subsequent operation that allows the attacker to observe the poisoned value

The CoCo trace only shows storage.set, with no corresponding storage.get → attacker-accessible output path. Storage poisoning alone without a retrieval mechanism is not exploitable per the methodology.

**Additional Context:** The manifest.json specifies `externally_connectable` with whitelist `["https://*.dscvrfans.com/*","http://localhost/*"]`, which means only those domains/extensions can send external messages. However, per the methodology, we ignore manifest restrictions and assume any attacker can trigger onMessageExternal if the listener exists. Even so, without a retrieval path, storage poisoning is not exploitable.
