import { useEffect, useState } from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  apiRequest,
  getStudentToken,
} from "../api/api";


function AdaptiveQuiz() {
  const navigate = useNavigate();

  const { topicId } =
    useParams();


  const [quizData, setQuizData] =
    useState(null);

  const [answers, setAnswers] =
    useState({});

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {
    startQuiz();
  }, [topicId]);


  async function startQuiz() {
    const token =
      getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResult(null);
      setAnswers({});

      const data =
        await apiRequest(
          `/quizzes/adaptive/?topic=${topicId}`,
          {
            token,
          }
        );

      setQuizData(data);

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  function selectAnswer(
    questionId,
    answer
  ) {
    setAnswers(
      (previous) => ({
        ...previous,
        [questionId]: answer,
      })
    );
  }


  async function submitQuiz() {
    if (!quizData) {
      return;
    }


    const questions =
      quizData.questions || [];


    const unanswered =
      questions.filter(
        (question) =>
          !answers[question.id]
      );


    if (unanswered.length) {
      setError(
        "Please answer every question before submitting."
      );

      return;
    }


    const payload =
      questions.map(
        (question) => ({
          question:
            question.id,

          answer:
            answers[
              question.id
            ],
        })
      );


    try {
      setSubmitting(true);
      setError("");

      const data =
        await apiRequest(
          "/quizzes/adaptive/submit/",
          {
            method: "POST",

            token:
              getStudentToken(),

            body: {
              session_id:
                quizData.session.id,

              answers:
                payload,
            },
          }
        );

      setResult(data);

    } catch (err) {
      setError(err.message);

    } finally {
      setSubmitting(false);
    }
  }


  if (loading) {
    return (
      <div className="dashboard-loading">
        Preparing adaptive quiz...
      </div>
    );
  }


  if (error && !quizData) {
    return (
      <div className="dashboard-error-page">

        <h2>
          Unable to start quiz
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


  /*
   * =======================================================
   * RESULT SCREEN
   * =======================================================
   */

  if (result) {
    const attempt =
      result.attempt;

    const mastery =
      result.mastery_after;


    return (
      <div className="quiz-page">

        <div className="quiz-container">

          <div className="result-card">

            <span className="dashboard-label">
              QUIZ COMPLETE
            </span>

            <h1>
              {
                result.topic.name
              }
            </h1>


            <div className="result-score">

              {
                attempt.percentage
              }%

            </div>


            <p>
              Score:
              {" "}
              {attempt.score}
              /
              {
                attempt.total_questions
              }
            </p>


            <div className="result-grid">

              <div>

                <span>
                  Mastery
                </span>

                <strong>
                  {
                    mastery.mastery_score
                  }%
                </strong>

              </div>


              <div>

                <span>
                  Level
                </span>

                <strong>
                  {
                    mastery.level
                  }
                </strong>

              </div>


              <div>

                <span>
                  Next Difficulty
                </span>

                <strong>
                  {
                    result
                      .next_adaptive_difficulty
                      .name
                  }
                </strong>

              </div>

            </div>


            <div className="result-actions">

              {
                mastery.level !==
                "strong" && (

                  <button
                    className="primary-button"
                    onClick={
                      startQuiz
                    }
                  >
                    Continue Adaptive Practice
                  </button>

                )
              }


              <button
                className="secondary-button"
                onClick={() =>
                  navigate(
                    `/student/topic/${topicId}`
                  )
                }
              >
                Back to Lesson
              </button>


              {
                mastery.level ===
                  "strong" && (

                  <button
                    className="success-button"
                    onClick={() =>
                      navigate(
                        "/student/dashboard"
                      )
                    }
                  >
                    Topic Mastered ✓
                  </button>

                )
              }

            </div>

          </div>

        </div>

      </div>
    );
  }


  const questions =
    quizData?.questions || [];


  return (
    <div className="quiz-page">

      <div className="quiz-container">

        <button
          className="back-button"
          onClick={() =>
            navigate(
              `/student/topic/${topicId}`
            )
          }
        >
          ← Lesson
        </button>


        <div className="quiz-header">

          <span className="dashboard-label">
            ADAPTIVE QUIZ
          </span>

          <h1>
            {
              quizData.quiz.title
            }
          </h1>

          <p>
            {
              quizData.topic.subject
            }
            {" • "}
            {
              quizData.topic.chapter
            }
          </p>


          <div className="quiz-badges">

            <span>
              Difficulty:
              {" "}
              <strong>
                {
                  quizData
                    .adaptive_selection
                    .difficulty
                }
              </strong>
            </span>

            <span>
              Current mastery:
              {" "}
              <strong>
                {
                  quizData
                    .mastery
                    .mastery_score
                }%
              </strong>
            </span>

          </div>

        </div>


        {questions.map(
          (question, index) => (

            <div
              className="question-card"
              key={question.id}
            >

              <span className="question-count">
                Question {index + 1}
                {" of "}
                {questions.length}
              </span>


              <h3>
                {
                  question.question_text
                }
              </h3>


              <div className="option-list">

                {[
                  [
                    "A",
                    question.option_a,
                  ],

                  [
                    "B",
                    question.option_b,
                  ],

                  [
                    "C",
                    question.option_c,
                  ],

                  [
                    "D",
                    question.option_d,
                  ],

                ].map(
                  ([
                    letter,
                    text,
                  ]) => (

                    <button
                      type="button"

                      key={letter}

                      className={
                        `option-button ${
                          answers[
                            question.id
                          ] === letter
                            ? "selected-option"
                            : ""
                        }`
                      }

                      onClick={() =>
                        selectAnswer(
                          question.id,
                          letter
                        )
                      }
                    >

                      <span>
                        {letter}
                      </span>

                      {text}

                    </button>

                  )
                )}

              </div>

            </div>

          )
        )}


        {error && (
          <div className="login-error">
            {error}
          </div>
        )}


        <button
          className="quiz-submit-button"
          onClick={submitQuiz}
          disabled={submitting}
        >

          {
            submitting
              ? "Submitting..."
              : "Submit Quiz"
          }

        </button>

      </div>

    </div>
  );
}


export default AdaptiveQuiz;