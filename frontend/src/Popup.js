/*global chrome*/
import React, { useState, useEffect } from "react";
// import ProgressBar from "react-bootstrap/ProgressBar";
import { ProgressBar } from "react-bootstrap";
import { Readability } from "@mozilla/readability";
import "./Popup.css";

const relatedArticlesEndpoint =
  "http://127.0.0.1:5000/getSearchResultsFromArticleTitle";
const resultsEndpoint = "http://127.0.0.1:5000/getBiasResult";

const Popup = () => {
  const [results, setResults] = useState([]);
  const [article, setArticle] = useState([]);
  const [relatedArticles, setRelatedArticles] = useState([]);
  const [color, setColor] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const getResults = async (allText) => {
    const fetchJsonRequest = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        article_text: allText,
      }),
    };
    fetch(resultsEndpoint, fetchJsonRequest)
      .then((res) => {
        console.log(res);
        return res.json();
      })
      .then((res) => {
        console.log(res);
        const leftOrRight = res.data.label;
        const curColor = leftOrRight === "Left" ? "blue" : "red";
        setColor(curColor);
        setResults(res.data);
        setIsLoading(false);
      })
      .catch((error) => {
        setIsLoading(false);
        console.log(error);
      });
  };

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
        return res.json();
      })
      .then((res) => {
        setRelatedArticles(res.data);
        setIsLoading(false);
      })
      .catch((error) => {
        setIsLoading(false);
        console.log(error);
      });
  };

  useEffect(() => {
    const bgPage = chrome.extension.getBackgroundPage();
    const dom = bgPage.dom;
    let curArticle = new Readability(dom).parse();
    setArticle(curArticle);
    getResults(curArticle.textContent);
    getRelatedArticles(curArticle.title);
  }, []);

  const LoadLater = () => {
    return (
      <div>
        <h1 className="result" style={{ color: color }}>
          {results.percentage}% {results.label} Leaning
        </h1>
        <div className="related-container">
          <h1 className="related-header">Related articles to read:</h1>
          {relatedArticles.map((relatedArticle) => {
            return (
              <a className="related-article" href={relatedArticle.url}>
                {relatedArticle.title}
              </a>
            );
          })}
        </div>
      </div>
    );
  };
  return (
    <div className="popup">
      <img
        className="logo"
        src={process.env.PUBLIC_URL + "/logo.png"}
        alt="img"
      />
      <h1 className="title" style={{ color: color }}>
        {article.title}
      </h1>
      <ProgressBar className="progress-container">
        <ProgressBar
          className="progress-left"
          now={
            results.label === "Left"
              ? results.percentage
              : 100 - results.percentage
          }
          key={1}
        />
        <ProgressBar
          className="progress-right"
          now={
            results.label === "Right"
              ? results.percentage
              : 100 - results.percentage
          }
          key={2}
        />
      </ProgressBar>
      {isLoading ? <h1 className="loading">Calculating...</h1> : <LoadLater />}
    </div>
  );
};

export default Popup;
