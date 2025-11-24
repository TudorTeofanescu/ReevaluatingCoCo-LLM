# CoCo Analysis: mgdjdlbnfpahekagnklllnmiphnlnled

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (bg_localStorage_setItem_value_sink - duplicate detections)

---

## Sink: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mgdjdlbnfpahekagnklllnmiphnlnled/opgen_generated_files/bg.js
Line 1143	    const serverIndex = servers.indexOf(message.domain);
	message.domain
Line 1143	    const serverIndex = servers.indexOf(message.domain);
	servers.indexOf(message.domain)
```

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1137-1167)
chrome.runtime.onMessageExternal.addListener(function (
  message,
  sender,
  sendResponse
) {
  if (message.type === "deepLink") {
    const serverIndex = servers.indexOf(message.domain); // ← attacker-controlled domain
    if (serverIndex === -1) {
      // Unsupported server
      sendResponse({ deepLink: false });
    } else {
      const doDeepLink = (focusOnly) => {
        sendResponse({ deepLink: true });
        chrome.tabs.remove(sender.tab.id, () => {
          if (chrome.runtime.lastError) {
            console.log(chrome.runtime.lastError.message);
          }
        });

        if (focusOnly) {
          focusAllWindows();
        } else {
          selectedServerIndex = serverIndex; // Sets internal variable
          openPopout(message.roomName); // Opens room
        }
      };
      // ... continues with logic
    }
  }
});

// Function called from above (bg.js Line 1031-1041)
window.openPopout = (newRoomName) => {
  roomName = newRoomName;
  domain = servers[selectedServerIndex]; // Uses validated serverIndex
  localStorage.setItem("serverSelect", selectedServerIndex); // Stores index (0-2)

  let recentRoomNames = JSON.parse(localStorage.getItem("recentRooms")) || [];
  recentRoomNames = recentRoomNames.filter((e) => e.roomName !== roomName);
  recentRoomNames.unshift({ roomName: roomName, timestamp: Date.now() });
  localStorage.setItem("recentRooms", JSON.stringify(recentRoomNames)); // Stores room list

  openedUrl = `https://${domain}/#/extId=${extId}/roomName=${roomName}`;
  window.mainAppWindowObject = window.open(openedUrl, ...);
};
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While external messages can trigger localStorage writes via `message.domain` and `message.roomName`, the attacker-controlled data undergoes validation before storage. The `message.domain` is validated against a hardcoded `servers` array (only indexOf result is stored, not the domain itself). The stored data (serverIndex integer and room names) does not flow back to the attacker - there is no retrieval path via sendResponse or postMessage. The localStorage is only used internally by the extension for its own functionality (remembering server selection and recent rooms). Storage poisoning alone without a retrieval path to the attacker is explicitly defined as FALSE POSITIVE in the methodology.

---

## Manifest Configuration

```json
"externally_connectable": {
  "matches": [
    "https://jip-hop.github.io/jitsi-pop/*",
    "https://jitsipop.tk/*"
  ]
}
```

**Note:** The extension only allows external messages from two specific whitelisted domains, and even if they could poison storage, there's no mechanism for the attacker to retrieve the poisoned data back.
