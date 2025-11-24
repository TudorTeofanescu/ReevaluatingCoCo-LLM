# CoCo Analysis: nkkmoejolocjebnfebdhoggjhmiibkej

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkkmoejolocjebnfebdhoggjhmiibkej/opgen_generated_files/cs_0.js
Line 622	window.addEventListener('message', function(event) {
Line 624	  if (event.source === window && event.data.type && event.data.type == "PCE_VOTE_SUCCESS") {
Line 627	      storeVoteUpdateUi(event.data.upvote);
```

**Code:**

```javascript
// Content script - cs_0.js (Line 622-652)
window.addEventListener('message', function(event) {
  if (event.source === window && event.data.type && event.data.type == "PCE_VOTE_SUCCESS") {
      console.log("Message received from injected script:", event.data);
      hideSpinner();
      storeVoteUpdateUi(event.data.upvote); // ← attacker-controlled
  }
});

function storeVoteUpdateUi(upvote) {
  storeVote(window.location.href, upvote); // ← flows to storage
  if (upvote === true) {
    document.querySelector('#pce-ext-inject .pce-ext-button.like').classList.add('voted');
  } else if (upvote === false) {
     document.querySelector('#pce-ext-inject .pce-ext-button.dislike').classList.add('voted');
  }
}

function storeVote(key, value) {
  var obj = {};
  obj[key] = value;
  chrome.storage.local.set(obj, function() {}); // Storage write sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path. The attacker can write `event.data.upvote` to storage, but there is no flow shown where this poisoned data is retrieved and sent back to the attacker or used in a subsequent vulnerable operation.
