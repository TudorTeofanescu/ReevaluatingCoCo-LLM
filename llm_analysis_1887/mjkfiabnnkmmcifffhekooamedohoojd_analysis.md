# CoCo Analysis: mjkfiabnnkmmcifffhekooamedohoojd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1: cs_window_eventListener_RedditBoost_StoreNameTags → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 480: window.addEventListener("RedditBoost_StoreNameTags", function(event)
Line 481: chrome.storage.sync.set(event.detail, function() {

**Code:**

```javascript
// Content script (onLoad.js / cs_0.js) - Entry point
window.addEventListener("RedditBoost_StoreNameTags", function(event) {
  chrome.storage.sync.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage (any site where extension runs: reddit.com)
// Attacker can dispatch custom event with arbitrary data
window.dispatchEvent(new CustomEvent("RedditBoost_StoreNameTags", {
  "detail": {
    "RedditBoost_NameTags": "attacker_controlled_data",
    "malicious_key": "malicious_value"
  }
}));
```

**Impact:** Storage poisoning. Attacker can write arbitrary key-value pairs to chrome.storage.sync, polluting the extension's storage with malicious data. While the stored data itself doesn't directly flow back to the attacker in this specific sink, it corrupts the extension's storage mechanism.

---

## Sink 2: cs_window_eventListener_RedditBoost_StoreCommentBans → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 496: window.addEventListener("RedditBoost_StoreCommentBans", function(event)
Line 497: chrome.storage.sync.set(event.detail, function() {

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("RedditBoost_StoreCommentBans", function(event) {
  chrome.storage.sync.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage on reddit.com
window.dispatchEvent(new CustomEvent("RedditBoost_StoreCommentBans", {
  "detail": {
    "RedditBoost_BlockedUserForComments": "attacker_data"
  }
}));
```

**Impact:** Storage poisoning. Attacker can manipulate the comment ban list, potentially unbanning malicious users or adding innocent users to the ban list.

---

## Sink 3: cs_window_eventListener_RedditBoost_StoreSubmissionBans → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 512: window.addEventListener("RedditBoost_StoreSubmissionBans", function(event)
Line 513: chrome.storage.sync.set(event.detail, function() {

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("RedditBoost_StoreSubmissionBans", function(event) {
  chrome.storage.sync.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage on reddit.com
window.dispatchEvent(new CustomEvent("RedditBoost_StoreSubmissionBans", {
  "detail": {
    "RedditBoost_BlockedUserForSubmissions": "attacker_data"
  }
}));
```

**Impact:** Storage poisoning. Attacker can manipulate the submission ban list.

---

## Sink 4: cs_window_eventListener_RedditBoost_StoreCssBans → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 528: window.addEventListener("RedditBoost_StoreCssBans", function(event)
Line 529: chrome.storage.sync.set(event.detail, function() {

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("RedditBoost_StoreCssBans", function(event) {
  chrome.storage.sync.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage on reddit.com
window.dispatchEvent(new CustomEvent("RedditBoost_StoreCssBans", {
  "detail": {
    "RedditBoost_BlockedCss": "attacker_data"
  }
}));
```

**Impact:** Storage poisoning. Attacker can manipulate the CSS ban list.

---

## Sink 5: cs_window_eventListener_RedditBoost_StoreSubredditBans → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 544: window.addEventListener("RedditBoost_StoreSubredditBans", function(event)
Line 545: chrome.storage.sync.set(event.detail, function() {

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("RedditBoost_StoreSubredditBans", function(event) {
  chrome.storage.sync.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage on reddit.com
window.dispatchEvent(new CustomEvent("RedditBoost_StoreSubredditBans", {
  "detail": {
    "RedditBoost_BlockedSubreddits": "attacker_data"
  }
}));
```

**Impact:** Storage poisoning. Attacker can manipulate the subreddit ban list.

---

## Sink 6: cs_window_eventListener_RedditBoost_StorePreviewedLinks → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjkfiabnnkmmcifffhekooamedohoojd/opgen_generated_files/cs_0.js
Line 559: window.addEventListener("RedditBoost_StorePreviewedLinks", function(event)
Line 560: chrome.storage.local.set(event.detail, function() {

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("RedditBoost_StorePreviewedLinks", function(event) {
  chrome.storage.local.set(event.detail, function() { // ← attacker-controlled via event.detail
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious webpage on reddit.com
window.dispatchEvent(new CustomEvent("RedditBoost_StorePreviewedLinks", {
  "detail": {
    "RedditBoost_PreviewedLinks": "attacker_data"
  }
}));
```

**Impact:** Storage poisoning. Attacker can manipulate the previewed links list in local storage.

---

## Overall Analysis

All 6 sinks represent TRUE POSITIVE vulnerabilities. The extension listens for custom DOM events in its content script without any validation. Since the content script runs on reddit.com pages, any malicious script on those pages (or injected via XSS) can dispatch these custom events with arbitrary data in the `event.detail` field. This data is then written directly to chrome.storage.sync or chrome.storage.local without sanitization, allowing storage poisoning attacks. While these specific flows only poison storage and don't immediately retrieve the data back to the attacker, the ability to write arbitrary data to extension storage is a security vulnerability that corrupts the extension's internal state and can be leveraged for further attacks.
