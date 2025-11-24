# CoCo Analysis: ofbdbafohbopbnaiknmgeijcbmdcpeji

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ofbdbafohbopbnaiknmgeijcbmdcpeji/opgen_generated_files/bg.js
Line 1114: `joinRoom(request.roomCode, request.password);`

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
      if (request.type === 'joinRoom') {
        joinRoom(request.roomCode, request.password); // ← attacker-controlled
        chrome.action.openPopup();
      }
    }
);

// joinRoom function
function joinRoom(roomCode, password) {
    socket.emit('joinRoom', { roomCode, password }, (response) => {
        if (response && response.success) {
            currentRoom = roomCode;
            currentPassword = password;
            chrome.storage.local.set({ roomCode, password }); // Storage sink
            sendMessageToPopup({type: 'roomJoined', roomCode, password});
        } else {
            sendMessageToPopup({type: 'error', message: 'Failed to join room: ' + (response ? response.message : 'Unknown error')});
        }
    });
}

// Only internal retrieval - no path back to attacker
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.get(['roomCode', 'password'], (result) => {
        if (result.roomCode && result.password) {
            joinRoom(result.roomCode, result.password); // Used internally only
        }
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. External messages from https://kakure.io/* can trigger storage.set via onMessageExternal, but the stored data is never retrieved back to the attacker. The only storage.get operation uses the data internally for auto-rejoining rooms on installation, with no path to send the data back to any external party.
