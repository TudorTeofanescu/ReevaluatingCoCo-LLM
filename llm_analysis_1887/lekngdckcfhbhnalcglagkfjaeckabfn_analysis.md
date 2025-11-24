# CoCo Analysis: lekngdckcfhbhnalcglagkfjaeckabfn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 7 (all related to same flow pattern)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lekngdckcfhbhnalcglagkfjaeckabfn/opgen_generated_files/cs_1.js
Line 1021: window.addEventListener('message', (event) => {
Line 1040: if (event.data.isAuthInitiated && authInitiated) {
Lines 1061-1067: Multiple event.data fields (test_id, candidate_id, test_token, test_name, email, candidate_name, org_key)

**Code:**

```javascript
// Content script (cs_1.js) - Lines 1021-1068
window.addEventListener('message', (event) => {
  // ... whitelist check on lines 1032-1039 ...
  if (event.data.isAuthInitiated && !authInitiated) {
    chrome.runtime.sendMessage({
      type: 'start-auth',
      test_id: event.data.test_id,        // ← attacker-controlled
      candidate_id: event.data.candidate_id,  // ← attacker-controlled
      test_token: event.data.test_token,    // ← attacker-controlled
      test_name: event.data.test_name,     // ← attacker-controlled
      email: event.data.email,            // ← attacker-controlled
      candidate_name: event.data.candidate_name, // ← attacker-controlled
      org_key: event.data.org_key,        // ← attacker-controlled
    });
  }
});

// Background script (bg.js) - Lines 2053-2065
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'start-auth') {
    chrome.storage.local.set(
      {
        test_id: request.test_id,
        candidate_id: request.candidate_id,
        test_token: request.test_token,
        test_name: request.test_name,
        email: request.email,
        candidate_name: request.candidate_name,
        org_key: request.org_key,
      },
      () => console.log('Trying to authenticate candidate...')
    );
    startAuthentication(request);
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. The attacker can write arbitrary data to chrome.storage.local via window.postMessage, but there is no retrieval path that sends the stored data back to the attacker. The extension only reads these values internally and removes them during cleanup (lines 2107-2114). The stored data is used in startAuthentication() to make a fetch request to the hardcoded backend URL (EXTENSION_API_URL + '/auth/exam/login'), which is trusted infrastructure. Storage poisoning without a retrieval path to the attacker is not exploitable per the methodology.
