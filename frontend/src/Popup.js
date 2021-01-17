/*global chrome*/
import React, { useState, useEffect } from "react";
// import ProgressBar from "react-bootstrap/ProgressBar";
import { ProgressBar } from "react-bootstrap";
import { Readability } from "@mozilla/readability";
import axios from "axios";
import "./Popup.css";

const relatedArticlesEndpoint =
  "http://127.0.0.1:5000/getSearchResultsFromBiasedArticle";
const resultsEndpoint = "http://127.0.0.1:5000/getResult";

const Popup = () => {
  const [results, setResults] = useState([]);
  const [article, setArticle] = useState([]);
  const [relatedArticles, setRelatedArticles] = useState([]);

  const getResults = async (allText) => {
    const res = await axios.get(resultsEndpoint, { allText: allText });
    console.log(res);
    setResults(res.data.data[0]);
  };

  const getRelatedArticles = async (title) => {
    // const res = await axios.post(relatedArticlesEndpoint, { title: title });
    const res = await axios.get(relatedArticlesEndpoint);
    setRelatedArticles(res.data.data[0].urls);
  };

  useEffect(() => {
    const bgPage = chrome.extension.getBackgroundPage();
    const dom = bgPage.dom;
    let curArticle = new Readability(dom).parse();
    setArticle(curArticle);
    getResults(curArticle.textContent);
    getRelatedArticles(curArticle.title);
  }, []);
  return (
    <div className="popup">
      <img
        className="logo"
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/736px-Google_2015_logo.svg.png"
        alt="img"
      />
      <h1 className="title">{article.title}</h1>
      <ProgressBar className="progress-container">
        <ProgressBar
          className="progress"
          striped
          variant="success"
          now={results.probability[0]}
          key={1}
        />
        <ProgressBar
          className="progress"
          variant="warning"
          now={results.probability[1]}
          key={2}
        />
      </ProgressBar>
      <h1 className="result">
        {Math.max(results.probability)}% {results.result} Leaning
      </h1>
      <div className="related-container">
        <h1 className="related-header">
          Suggested articles related to{" "}
          <span className="title">{article.title}</span>:
        </h1>
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
