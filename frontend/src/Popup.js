/*global chrome*/

import React, { useState, useEffect } from "react";
import { Readability } from "@mozilla/readability";

const Popup = () => {
  const [article, setArticle] = useState([]);
  useEffect(() => {
    const bgPage = chrome.extension.getBackgroundPage();
    const dom = bgPage.dom;
    let curArticle = new Readability(dom).parse();
    setArticle(curArticle.title);
  });
  return (
    <div>
      <h1>{article}</h1>
    </div>
  );
};

export default Popup;
