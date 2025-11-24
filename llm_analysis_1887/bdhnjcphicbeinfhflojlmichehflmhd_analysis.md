# CoCo Analysis: bdhnjcphicbeinfhflojlmichehflmhd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (5+ duplicate instances of same flow pattern)

---

## Sink: XMLHttpRequest_responseText_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdhnjcphicbeinfhflojlmichehflmhd/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1174: let connections = JSON.parse(request.responseText).data
Line 1183: port.postMessage({ data: connections[0] })

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdhnjcphicbeinfhflojlmichehflmhd/opgen_generated_files/cs_0.js
Line 497-511: Various data extractions (getName, getPersonalScore, getMostConnectedScore)
Line 684: $('#sixDosCard').html(card) // jQuery html sink

**Code:**

```javascript
// Background script - sendSearchRequest function (bg.js, lines 1167-1188)
const contactApiUrl = 'https://contacts-api.6dos.co'; // ← Hardcoded backend URL

function sendSearchRequest (port, token, params, type) {
  let request = new XMLHttpRequest()
  request.open('POST', `${contactApiUrl}/v1/contacts/search`) // ← Hardcoded backend
  request.setRequestHeader('Content-type', 'application/json; charset=utf-8');
  request.setRequestHeader('Authorization', 'Bearer ' + token)
  request.onreadystatechange = () => {
    if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
      let connections = JSON.parse(request.responseText).data // Data from backend
      if (connections.length === 0) {
        port.postMessage({ error: 'No connections were found!', data: {}, type: type })
      } else if (connections.length > 1) {
        port.postMessage({ error: 'Multiple connections were found!', data: {}, type: type })
      } else {
        port.postMessage({ data: connections[0] }) // Send to content script
      }
    }
  }
  request.send(params)
}

// Content script - receives data from background (cs_0.js, lines 473-479)
port.onMessage.addListener((msg) => {
  if (msg.error && msg.type === 'standard') {
    linkedInURLSearch()
  } else {
    injectSixDos(msg.data) // Calls updateCard -> renderConnectionInfo
  }
})

// Content script - renders connection info (cs_0.js, lines 666-685)
function renderConnectionInfo(connectionInfo) {
  let name = getName(connectionInfo) // Extracts connectionInfo.info
  let jobTitle = getJobTitle(connectionInfo)
  let company = getCompany(connectionInfo)
  let personalScore = getPersonalScore(connectionInfo)
  let mostConnectedScore = getMostConnectedScore(connectionInfo) // Extracts connectionInfo.scores[0].score

  let card =
  `
  <div class="conn-info">
    <span class="name-text">${name}</span><br/>
    ${jobTitle}
    ${company}
    <span class="score-text">Most Connected Score: ${mostConnectedScore}</span><br />
    ${personalScore}
  </div>
  `

  $('#sixDosCard').html(card) // jQuery html sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** The data flows from a hardcoded developer backend URL (https://contacts-api.6dos.co/v1/contacts/search) to the UI via jQuery .html(). This is trusted infrastructure - the extension fetches connection data from its own backend API and displays it on LinkedIn profiles. There is no external attacker entry point; the content script scrapes LinkedIn profile info and sends it to the background, which queries the extension's own backend. Compromising the developer's backend infrastructure is a separate issue from extension vulnerabilities.
