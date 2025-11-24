# CoCo Analysis: kjhgiknbbelnfpbliecglhiedkbhbjeb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple window_postMessage_sink detections (all related to HistoryItem_source)

---

## Sink: HistoryItem_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kjhgiknbbelnfpbliecglhiedkbhbjeb/opgen_generated_files/bg.js
Lines 775-783: Mock HistoryItem object creation in CoCo framework code
Line 1042-1043: browser.history.search and port.postMessage in actual extension code

**Code:**

```javascript
// Background script - Response handler (bg.js, line 1034-1045)
[MSG.GET_RECENT_WEBSITES] (port) {
  browser.permissions.contains({
    permissions: ['history'],
    origins: [APP_URL]  // APP_URL = 'https://app.tabitab.com/'
  }, (granted) => {
    if(!granted) {
      return port.postMessage(0)
    }
    browser.history.search({text: ''}, websites => {
      port.postMessage(websites)  // History data sent to content script
    })
  })
}

// Content script - Message listener (cs_0.js, line 546-553)
[MSG.GET_RECENT_WEBSITES] (e) {
  fetchRecentWebsites.then(websites => {
    if(websites === 0) { throw new Error() }
    e.source.postMessage({type: MSG.RECENT_WEBSITES, websites}, e.origin)  // History sent to webpage
  })
  .catch(err => {
    e.source.postMessage({type: 'NO_PERMISSION', data:"history"}, e.origin)
  })
}

// Content script - Window message listener (cs_0.js, line 564-572)
window.addEventListener('message', e => {
  if(!e.data || !e.origin.includes(APP_URL.substr(0, APP_URL.length - 1))) { return }  // Origin check
  let data = e.data
  try {
    if(data.type) {
      windowResponses[data.type](e)
    }
  } catch(e) {}
})
```

**Classification:** FALSE POSITIVE

**Reason:** The extension only accepts window messages from its own trusted domain (https://app.tabitab.com) as enforced by the origin check on line 565. The content script only runs on `*://*.tabitab.com/*` as specified in manifest.json. While the extension does send sensitive history data via window.postMessage, it only does so to the developer's own website, which is trusted infrastructure. Data flowing to hardcoded backend/frontend URLs controlled by the developer is not considered an attacker-controllable vulnerability under our threat model.
