import { useEffect, useState } from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  apiRequest,
  getStudentToken,
  normalizeList,
} from "../api/api";


function TopicLesson() {
  const navigate = useNavigate();

  const { topicId } = useParams();

  const [content, setContent] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    loadContent();
  }, [topicId]);


  async function loadContent() {
    const token =
      getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response =
        await apiRequest(
          `/courses/learning-content/?topic=${topicId}`,
          {
            token,
          }
        );

      const items =
        normalizeList(response);

      if (!items.length) {
        throw new Error(
          "Learning content is not available for this topic."
        );
      }

      setContent(
        items[0]
      );

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading lesson...
      </div>
    );
  }


  if (error) {
    return (
      <div className="dashboard-error-page">

        <h2>
          Unable to load lesson
        </h2>

        <p>
          {error}
        </p>

        <button
          className="primary-button"
          onClick={() =>
            navigate(-1)
          }
        >
          Go Back
        </button>

      </div>
    );
  }


  return (
    <div className="lesson-page">

      <div className="lesson-container">

        <button
          className="back-button"
          onClick={() =>
            navigate(-1)
          }
        >
          ← Topics
        </button>


        <div className="lesson-heading">

          <span className="dashboard-label">
            {
              content.subject_name
            }
            {" • "}
            {
              content.chapter_name
            }
          </span>

          <h1>
            {
              content.topic_name
            }
          </h1>

        </div>


        <section className="lesson-block">

          <h2>
            Explanation
          </h2>

          <p>
            {
              content.explanation
            }
          </p>

        </section>


        <section className="lesson-block">

          <h2>
            Key Concepts
          </h2>

          <p>
            {
              content.key_concepts
            }
          </p>

        </section>


        <section className="lesson-block">

          <h2>
            Easy Method
          </h2>

          <p>
            {
              content.easy_method
            }
          </p>

        </section>


        <section className="lesson-block">

          <h2>
            Worked Example
          </h2>

          <p>
            {
              content.worked_example
            }
          </p>

        </section>


        <section className="lesson-block warning-block">

          <h2>
            Common Mistakes
          </h2>

          <p>
            {
              content.common_mistakes
            }
          </p>

        </section>


        <div className="lesson-quiz-box">

          <div>

            <span className="dashboard-label">
              ADAPTIVE ASSESSMENT
            </span>

            <h2>
              Ready to test your understanding?
            </h2>

            <p>
              Your quiz difficulty changes
              automatically according to
              your mastery.
            </p>

          </div>


          <button
            className="primary-button"
            onClick={() =>
              navigate(
                `/student/topic/${topicId}/quiz`
              )
            }
          >
            Start Adaptive Quiz
          </button>

        </div>

      </div>

    </div>
  );
}


export default TopicLesson;