/*global chrome*/

console.log("background running");

chrome.runtime.onMessage.addListener(receiver);

function receiver(request, sender, sendResponse) {
  console.log("HI");
  console.log(request);
  document.documentElement.innerHTML = request.dom;
  dom = document;
}

// chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
//   console.log("Hi");
//   if (msg.foo == "bar") {
//     sendResponse("Test worked");
//   }
// });

// chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
//   console.log("Hi");
//   if (msg.foo === "bg") {
//     console.log(2);
//     // chrome.tabs
//     //   .sendMessage({ type: "dom" }, (response) => {
//     //     return response;
//     //   })
//     //   .then((response) => sendResponse(response));
//   }
// });
