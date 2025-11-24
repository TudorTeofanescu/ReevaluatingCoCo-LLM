# CoCo Analysis: deepanfkojflalfajnkcnlhiejeomdgk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 10 (all chrome_storage_local_set_sink from cs_window_eventListener_message)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**

All 10 detections follow the same pattern across two content scripts (cs_1.js and cs_9.js):

From cs_1.js:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/deepanfkojflalfajnkcnlhiejeomdgk/opgen_generated_files/cs_1.js
Line 494: window.addEventListener('message', function (event) {
Line 495: console.log('Received message from parent window:', event.data);
Line 503: console.log('auth token:', event.data.content.message.authToken);
Line 508-511: Storage.local.set with various fields from event.data
```

From cs_9.js (same pattern):
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/deepanfkojflalfajnkcnlhiejeomdgk/opgen_generated_files/cs_9.js
Line 472-497: Identical code pattern
```

The fields detected are:
1. authToken: event.data.content.message.authToken
2. is_active_patron: event.data.content.message.is_active_patron
3. name: event.data.content.message.name
4. profile_picture_url: event.data.content.message.profile_picture_url
5. email_address: event.data.content.message.email_address

**Code:**

```javascript
// Content script - window message listener (cs_1.js lines 494-521)
window.addEventListener('message', function (event) {
  console.log('Received message from parent window:', event.data);

  // Responds to extension check (no origin validation)
  if (event.data.type === 'EXAMRIPPER_CHECK') {
    console.log('EXAMRIPPER_CHECK');
    window.postMessage({ type: 'EXAMRIPPER_EXTENSION' }, '*');
  }

  // Storage write - protected by origin check
  if (event.origin === 'https://beta.examripper.com') { // ← origin validation
    console.log('auth token:', event.data.content.message.authToken);
    console.log('donor status:', event.data.content.message.is_active_patron);

    chrome.storage.local.set(
      {
        name: event.data.content.message.name,                      // ← attacker-controlled (if from beta.examripper.com)
        pfp: event.data.content.message.profile_picture_url,        // ← attacker-controlled
        donor_status: event.data.content.message.is_active_patron,  // ← attacker-controlled
        email: event.data.content.message.email_address,            // ← attacker-controlled
        authToken: event.data.content.message.authToken,            // ← attacker-controlled
        lite: event.data.content.message.lite || false,             // ← attacker-controlled
      },
      function () {
        console.log('Data is saved to local storage.');
      }
    );
  }
});

// Background script - Storage retrieval (lines 1098-1101)
// Storage is read but only sent to extension's own tabs, NOT back to external caller
chrome.runtime.onMessage.addListener((message, sender) => {
  if (sender.tab?.id) {
    switch (message.action) {
      case 'Edpuzzle_GetClickToAnswer':
        chrome.storage.local.get('edpuzzle_clickToAnswer', ({ edpuzzle_clickToAnswer }) => {
          const enabled = typeof edpuzzle_clickToAnswer === 'boolean' ? edpuzzle_clickToAnswer : false;
          chrome.tabs.sendMessage(tab_id, Message('Edpuzzle_ClickToAnswer', { enabled })); // ← sent to tab, not external
        });
        break;
    }
  }
});

// Storage also used to determine popup page (lines 1108-1112)
chrome.storage.local.get(['donor_status'], function ({ donor_status }) {
  if (donor_status === true) {
    chrome.action.setPopup({ tabId, popup: '/popup/loggedInSub.html' });
  } else {
    chrome.action.setPopup({ tabId, popup: '/popup/start.html' });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While an attacker controlling beta.examripper.com (or with XSS on that domain) can poison the storage via window.postMessage, there is no retrieval path for the attacker to get the data back. The stored data is only used internally by the extension:
1. To determine which popup page to display (popup/loggedInSub.html vs popup/start.html)
2. To send configuration to the extension's own tabs via chrome.tabs.sendMessage (not to external callers)
3. No sendResponse with stored data sent back to the attacker
4. No postMessage sending stored data to attacker-controlled origins
5. No fetch() to attacker-controlled URLs with stored data

Per the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT a vulnerability - data must flow back to attacker to be exploitable." The attacker can write to storage but cannot retrieve the poisoned values, making this unexploitable.
