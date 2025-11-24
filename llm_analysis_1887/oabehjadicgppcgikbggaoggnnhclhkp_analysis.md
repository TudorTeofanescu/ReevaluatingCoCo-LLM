# CoCo Analysis: oabehjadicgppcgikbggaoggnnhclhkp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 5

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (Posts)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oabehjadicgppcgikbggaoggnnhclhkp/opgen_generated_files/cs_1.js
Line 748	async function handleEvent(event) {
Line 654	  if (event.data.action == "redirectResponse") {
Line 670	        response: event.data.response,
Line 759	        const posts = parsed.response.Posts;

**Code:**

```javascript
// Content script - lines 748-796
async function handleEvent(event) {
  let parsed = parseEvent(event);  // ← event.data from window.postMessage
  if (parsed != null) {
    if (parsed.retryAfter !== undefined) {
      // ... retry logic
    } else {
      let postsTails = ["query-consular-posts", "query-ofc-posts"];
      if (postsTails.includes(parsed.tail)) {
        const posts = parsed.response.Posts;  // ← attacker-controlled data
        chrome.storage.local.set({ posts: posts });  // Storage poisoning
      }
      // ... more storage.set calls
    }
  }
}
window.addEventListener("message", handleEvent);

// Later: Storage retrieval
async function submitContribution() {
  const storage = await chrome.storage.local.get(null);  // Get poisoned data
  const contrib = prepareContribution(storage);

  let options = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(contrib),  // ← poisoned data
  };
  fetch("https://visaslots.info/contribute", options)  // ← hardcoded backend URL
    .then((response) => response.json())
    .then((response) => {
      // Response from backend, not sent back to attacker
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is an incomplete storage exploitation chain. While the attacker can poison storage via postMessage, the stored data only flows to the hardcoded backend URL "https://visaslots.info/contribute" (trusted infrastructure), not back to the attacker. There is no sendResponse, postMessage, or attacker-accessible output path for the poisoned data.

---

## Sink 2-5: cs_window_eventListener_message → chrome_storage_local_set_sink (Members, HasError, ErrorString, ScheduleDays)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oabehjadicgppcgikbggaoggnnhclhkp/opgen_generated_files/cs_1.js
Line 769	        const members = parsed.response.Members;
Line 783	        storage.posts[index].HasError = parsed.response.HasError;
Line 784-787	        storage.posts[index].ErrorString = new DOMParser().parseFromString(parsed.response.ErrorString, "text/html").body.innerText;
Line 781	        storage.posts[index].Days = parsed.response.ScheduleDays;

**Code:**

```javascript
// Content script - continuation of handleEvent
      let membersTails = [
        "query-family-members-consular",
        "query-family-members-consular-reschedule",
        "query-family-members-ofc",
        "query-family-members-ofc-reschedule",
      ];
      if (membersTails.includes(parsed.tail)) {
        const members = parsed.response.Members;  // ← attacker-controlled
        chrome.storage.local.set({ members: members });  // Storage poisoning
      }
      let scheduleDaysTails = [
        "get-family-consular-schedule-days",
        "get-family-ofc-schedule-days",
      ];
      if (scheduleDaysTails.includes(parsed.tail)) {
        const storage = await chrome.storage.local.get("posts");
        const index = storage.posts.findIndex(
          (post) => post.ID === parsed.params.postId
        );
        storage.posts[index].Days = parsed.response.ScheduleDays;  // ← attacker-controlled
        storage.posts[index].Updated = Date.now();
        storage.posts[index].HasError = parsed.response.HasError;  // ← attacker-controlled
        storage.posts[index].ErrorString = new DOMParser().parseFromString(
          parsed.response.ErrorString,  // ← attacker-controlled
          "text/html"
        ).body.innerText;
        chrome.storage.local.set(storage);  // Storage poisoning
        await showDates(parsed);
        await submitContribution();  // Sends to hardcoded backend only
      }
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation. All poisoned storage data only flows to the hardcoded backend URL "https://visaslots.info/contribute" (trusted infrastructure). No retrieval path back to the attacker exists.
