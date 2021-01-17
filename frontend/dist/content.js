/*global chrome*/
console.log("Chrome extension ready to go?");

const message = {
  type: "content",
  dom: document.documentElement.innerHTML,
};
console.log(document);
chrome.runtime.sendMessage(message);
