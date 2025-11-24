# CoCo Analysis: ilkffbmaihmminbnoolhmcobojcolboj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ilkffbmaihmminbnoolhmcobojcolboj/opgen_generated_files/bg.js
Line 970	saveSurvey(message.survey, message.mappers);
```

**Code:**

```javascript
// Background script (bg.js) - Lines 967-988
chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
  switch (message.action) {
    case 'send_survey':
      saveSurvey(message.survey, message.mappers); // ← attacker-controlled data
      sendResponse({ installed: true });
      break;
  }
});

const saveSurvey = async (survey, mappers) => {
  try {
    // Store the data in Chrome storage
    chrome.storage.local.set({ survey, mappers }, () => { // Storage sink
      console.log('Survey has been stored.', survey, mappers);
    });
    await chrome.action.setBadgeText({ text: 'ON' });
  } catch (error) {
    console.error('Error fetching survey:', error);
  }
};

// Internal message handler - retrieval (line 996-1002)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'get_survey':
      chrome.storage.local.get(['survey', 'mappers']).then(sendResponse); // Returns to internal caller only
      return true;
  }
});

// Content script (cs_0.js) - Lines 612-624, injected into https://prson-srpel.apps.cic.gc.ca/*
const generateMapper = async (immType) => {
  try {
    response = await chrome.runtime.sendMessage({ action: 'get_survey' }); // Internal retrieval
    _survey = response.survey;
    _mapper = JSON.parse(m.content);
    // Data used internally to populate government forms, NOT sent back to external attacker
  } catch (error) {
    console.error('Error fetching survey:', error);
  }
};
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While external messages can write attacker-controlled data to chrome.storage.local (lines 967-979), there is no retrieval path that returns the poisoned data back to the attacker. The storage retrieval is only accessible via chrome.runtime.onMessage (internal messages, line 996-1002), not onMessageExternal. The content script retrieves the stored data (line 614) but only uses it internally to auto-fill forms on the government website (https://prson-srpel.apps.cic.gc.ca/*). There is no postMessage, sendResponse to external sources, or fetch to attacker-controlled URLs that would allow the attacker to retrieve the stored data. Per the methodology, storage poisoning alone without a retrieval path is NOT a vulnerability.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

Same as Sink 1 (tracks message.mappers instead of message.survey, but same flow).

**Classification:** FALSE POSITIVE
