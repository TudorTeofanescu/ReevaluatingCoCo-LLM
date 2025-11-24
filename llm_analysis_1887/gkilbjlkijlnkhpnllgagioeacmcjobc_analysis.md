# CoCo Analysis: gkilbjlkijlnkhpnllgagioeacmcjobc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: management_getSelf_source → sendResponseExternal_sink

**CoCo Trace:**
```
No line numbers provided by CoCo for this flow
```

**Classification:** FALSE POSITIVE

**Reason:** CoCo did not provide specific line numbers for this trace, and examining the code shows no actual flow where `chrome.management.getSelf()` data is sent back via `sendResponseExternal`. The management API at line 967 is used only to determine if it's a development install to set the server_host, but this data is not sent to external callers. This appears to be a CoCo framework artifact without a real vulnerability.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkilbjlkijlnkhpnllgagioeacmcjobc/opgen_generated_files/bg.js
Line 980    if (request.jwt) {
    request.jwt
```

**Code:**

```javascript
// Background script (bg.js, lines 967-987) - Entry point
chrome.management.getSelf((self) => {
    console.log(self.installType)
    if (self.installType === 'development') {
        var server_host = "http://127.0.0.1:8000";
    } else {
        var server_host = "https://bukios.com";
    }
    chrome.storage.sync.set({server_host: server_host}, function() {
        console.log('server_host : ' + server_host);
    });
})

// External message handler - VULNERABLE
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.jwt) { // ← attacker-controlled from external message
        console.log('Token ::: ', request.jwt);
        sendResponse({ success: true, message: 'Token has been received' });
        chrome.storage.sync.set({jwt: request.jwt}, function() { // ← STORAGE POISONING
          console.log('Value is set to ' + request.jwt);
        });
    }
});

// Popup script (popup.js) - Storage retrieval and exploitation
chrome.storage.sync.get(['server_host'], function(result) {
    document.getElementById('loginButton').addEventListener('click',function(){
        chrome.tabs.create({ url: result.server_host + "/accounts/login/" }); // ← Uses poisoned server_host
    });
});

chrome.storage.sync.get(['jwt'], function(result) {
    if (result.jwt) { // ← Checks poisoned jwt
        page_add_bookmark(); // Shows bookmark form
    } else {
        page_login(); // Shows login button
    }
});

// Add bookmark function
function add_bookmark() {
    chrome.storage.sync.get(['server_host'], function(result) {
        if (result.server_host) {
            server_host = result.server_host; // ← Uses poisoned server_host
        } else {
            server_host = "https://bukios.com";
        }

        var postUrl = server_host + '/api/bookmarks/'; // ← Constructs URL with poisoned host
        var xhr = new XMLHttpRequest();
        xhr.open('POST', postUrl, true); // ← SSRF to attacker-controlled URL

        // ... sends bookmark data to poisoned URL
        xhr.send(JSON.stringify({ "url": url.value, "tags":  tags.value}));
    });
}
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
    "matches": [
        "*://bukios.com/*"
    ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted origin (bukios.com) can send arbitrary JWT data via chrome.runtime.onMessageExternal. The extension stores this data in chrome.storage.sync without validation.

**Attack:**

```javascript
// Malicious code on bukios.com (or compromised page on that domain)
// Attack: Poison both jwt and server_host storage values

// First, send fake JWT to bypass authentication check
chrome.runtime.sendMessage(
    'gkilbjlkijlnkhpnllgagioeacmcjobc',  // extension ID
    {jwt: {token: 'fake', username: 'attacker'}},
    function(response) {
        console.log('JWT poisoned:', response);
    }
);

// The extension also trusts chrome.management.getSelf to set server_host,
// but an attacker who compromises bukios.com can:
// 1. Set fake JWT to make extension think user is logged in
// 2. When user tries to save bookmark, redirect to attacker server

// Alternative: If attacker can also poison server_host somehow, they can
// redirect login button clicks and bookmark submissions to attacker.com
```

**Impact:** Complete storage exploitation chain with multiple attack vectors:

1. **Authentication Bypass**: Attacker can set fake JWT value, making the extension think the user is authenticated. This changes the UI from showing a login button to showing the bookmark form.

2. **Phishing**: The poisoned `server_host` is used in `chrome.tabs.create()` at popup.js line 7, so clicking the login button opens attacker-controlled URL instead of legitimate bukios.com login page.

3. **Data Exfiltration via SSRF**: When user saves a bookmark, the extension reads `server_host` from storage and sends bookmark data (URL and tags) to the poisoned server via XHR POST at popup.js line 91. Attacker receives user's browsing data.

4. **Persistent Compromise**: The poisoned values are stored in chrome.storage.sync, which persists across browser sessions and even syncs across the user's devices if Chrome sync is enabled.

The vulnerability exists because:
- External messages from bukios.com are trusted without validation
- Storage values are used directly in security-sensitive operations (URL construction, authentication checks)
- No integrity checks on stored values before use
