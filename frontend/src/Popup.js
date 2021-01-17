/*global chrome*/
import React, { useState, useEffect } from "react";
// import ProgressBar from "react-bootstrap/ProgressBar";
import { ProgressBar } from "react-bootstrap";
import { Readability } from "@mozilla/readability";
import "./Popup.css";

const relatedArticlesEndpoint =
  "http://127.0.0.1:5000/getSearchResultsFromArticleTitle";
const resultsEndpoint = "http://127.0.0.1:5000/getResult";

const Popup = () => {
  const [results, setResults] = useState([]);
  const [article, setArticle] = useState([]);
  const [relatedArticles, setRelatedArticles] = useState([]);

  const getResults = async (allText) => {};

  const getRelatedArticles = async (title) => {
    const fetchJsonRequest = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title,
      }),
    };
    fetch(relatedArticlesEndpoint, fetchJsonRequest)
      .then((res) => {
        console.log(res);
        return res.json();
      })
      .then((res) => setRelatedArticles(res.data[0].urls))
      .catch((error) => console.log(error));
  };

  useEffect(() => {
    const bgPage = chrome.extension.getBackgroundPage();
    const dom = bgPage.dom;
    let curArticle = new Readability(dom).parse();
    setArticle(curArticle);
    // getResults(curArticle.textContent);
    getRelatedArticles(curArticle.title);
  }, []);
  return (
    <div className="popup">
      <img
        className="logo"
        src={process.env.PUBLIC_URL + "/logo.png"}
        alt="img"
      />
      <h1 className="title">{article.title}</h1>
      <ProgressBar className="progress-container">
        <ProgressBar
          className="progress"
          striped
          variant="success"
          now={30}
          key={1}
        />
        <ProgressBar className="progress" variant="warning" now={60} key={2} />
      </ProgressBar>
      <h1 className="result">
        {Math.max(results.probability)}% {results.result} Leaning
      </h1>
      <div className="related-container">
        <h1 className="related-header">Related articles to read:</h1>
        {relatedArticles.map((relatedArticle) => {
          return (
            <a className="related-article" href={relatedArticle}>
              {relatedArticle}
            </a>
          );
        })}
      </div>
    </div>
  );
};

export default Popup;
