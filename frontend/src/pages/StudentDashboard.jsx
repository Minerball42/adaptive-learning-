import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  apiRequest,
  getStudentToken,
  removeStudentToken,
} from "../api/api";


function StudentDashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    loadDashboard();
  }, []);


  async function loadDashboard() {
    const token = getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    try {
      setLoading(true);

      const data = await apiRequest(
        "/progress/dashboard/",
        {
          token,
        }
      );

      setDashboard(data);

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  function logout() {
    removeStudentToken();

    localStorage.removeItem(
      "student_profile"
    );

    navigate("/student/login");
  }


  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading your dashboard...
      </div>
    );
  }


  if (error) {
    return (
      <div className="dashboard-error-page">

        <h2>
          Unable to load dashboard
        </h2>

        <p>{error}</p>

        <button
          onClick={loadDashboard}
          className="primary-button"
        >
          Try Again
        </button>

      </div>
    );
  }


  if (!dashboard) {
    return null;
  }


  const {
    student,
    overview,
    subject_progress = [],
    continue_learning,
    recommendations = [],
    recent_activity = [],
  } = dashboard;


  return (
    <div className="dashboard-page">

      {/* ================================================
          SIDEBAR
      ================================================= */}

      <aside className="dashboard-sidebar">

        <div className="dashboard-brand">

          <div className="brand-icon">
            AL
          </div>

          <div>
            <strong>
              Adaptive Learning
            </strong>

            <span>
              KSEAB Class 10
            </span>
          </div>

        </div>


        <nav className="dashboard-nav">

          <button className="nav-item active">
            Dashboard
          </button>

          <button className="nav-item">
            My Subjects
          </button>

          <button className="nav-item">
            Learning Path
          </button>

          <button className="nav-item">
            Progress
          </button>

        </nav>


        <button
          className="logout-button"
          onClick={logout}
        >
          Sign Out
        </button>

      </aside>


      {/* ================================================
          MAIN CONTENT
      ================================================= */}

      <main className="dashboard-main">

        <header className="dashboard-header">

          <div>
            <p className="dashboard-label">
              STUDENT DASHBOARD
            </p>

            <h1>
              Welcome back,
              {" "}
              {
                student?.username ||
                "Student"
              }
            </h1>

            <p>
              Continue your personalized
              learning journey.
            </p>
          </div>


          <div className="student-info">

            <strong>
              {student?.grade}
            </strong>

            <span>
              {student?.school}
            </span>

          </div>

        </header>


        {/* ================================================
            OVERVIEW
        ================================================= */}

        <section className="overview-grid">

          <div className="overview-card">
            <span>
              Overall Progress
            </span>

            <strong>
              {
                overview
                  ?.topic_completion_percentage
              }%
            </strong>

            <small>
              {
                overview
                  ?.completed_topics
              }
              {" / "}
              {
                overview
                  ?.total_topics
              }
              {" topics completed"}
            </small>
          </div>


          <div className="overview-card">
            <span>
              Completed Topics
            </span>

            <strong>
              {
                overview
                  ?.completed_topics
              }
            </strong>

            <small>
              Mastered topics
            </small>
          </div>


          <div className="overview-card">
            <span>
              Available Topics
            </span>

            <strong>
              {
                overview
                  ?.available_topics
              }
            </strong>

            <small>
              Ready to study
            </small>
          </div>


          <div className="overview-card">
            <span>
              Chapters
            </span>

            <strong>
              {
                overview
                  ?.completed_chapters
              }
              /
              {
                overview
                  ?.total_chapters
              }
            </strong>

            <small>
              Chapters completed
            </small>
          </div>

        </section>


        {/* ================================================
            CONTINUE LEARNING
        ================================================= */}

        {
          continue_learning && (
            <section className="continue-card">

              <div>
                <span className="section-badge">
                  CONTINUE LEARNING
                </span>

                <h2>
                  {
                    continue_learning
                      .topic_name
                  }
                </h2>

                <p>
                  {
                    continue_learning
                      .subject_name
                  }
                  {" • "}
                  {
                    continue_learning
                      .chapter_name
                  }
                </p>
              </div>


              <button
                className="primary-button"
                onClick={() =>
                  navigate(
                    `/student/topic/${continue_learning.topic_id}`
                  )
                }
              >
                Continue
              </button>

            </section>
          )
        }


        {/* ================================================
            SUBJECT PROGRESS
        ================================================= */}

        <section className="dashboard-section">

          <div className="section-heading">

            <div>
              <h2>
                My Subjects
              </h2>

              <p>
                Your progress across selected
                subjects.
              </p>
            </div>

          </div>


          <div className="subject-grid">

            {
              subject_progress.map(
                (subject) => (

                    <div
  className="subject-card clickable-card"
  key={subject.subject_id}
  onClick={() =>
    navigate(
      `/student/subject/${subject.subject_id}/chapters?name=${encodeURIComponent(
        subject.subject_name
      )}`
    )
  }
>
                    <div className="subject-card-top">

                      <div>
                        <span className="subject-type">
                          {
                            subject
                              .subject_type_display
                          }
                        </span>

                        <h3>
                          {
                            subject
                              .subject_name
                          }
                        </h3>

                        <p>
                          {
                            subject.total_chapters
                          }
                          {" chapters • "}
                          {
                            subject.total_topics
                          }
                          {" topics"}
                        </p>
                      </div>


                      <strong className="subject-percentage">
                        {
                          subject
                            .completion_percentage
                        }%
                      </strong>

                    </div>


                    <div className="progress-track">

                      <div
                        className="progress-fill"
                        style={{
                          width:
                            `${subject.completion_percentage}%`,
                        }}
                      />

                    </div>


                    <div className="subject-stats">

                      <span>
                        {
                          subject
                            .completed_topics
                        }
                        {" completed"}
                      </span>

                      <span>
                        {
                          subject
                            .remaining_topics
                        }
                        {" remaining"}
                      </span>

                    </div>

                  </div>

                )
              )
            }

          </div>

        </section>


        {/* ================================================
            BOTTOM GRID
        ================================================= */}

        <section className="dashboard-bottom-grid">

          {/* RECOMMENDATIONS */}

          <div className="dashboard-panel">

            <div className="section-heading">

              <div>
                <h2>
                  Recommended For You
                </h2>

                <p>
                  Personalized next steps.
                </p>
              </div>

            </div>


            {
              recommendations.length === 0
                ? (
                    <p className="empty-text">
                      No recommendations yet.
                    </p>
                  )
                : (
                    <div className="recommendation-list">

                      {
                        recommendations.map(
                          (item) => (

                            <div
                              className="recommendation-item"
                              key={
                                item.topic_id
                              }
                            >

                              <div>

                                <strong>
                                  {
                                    item
                                      .topic_name
                                  }
                                </strong>

                                <span>
                                  {
                                    item
                                      .subject_name
                                  }
                                  {" • "}
                                  {
                                    item
                                      .chapter_name
                                  }
                                </span>

                              </div>


                              <small>
                                {
                                  item
                                    .recommended_difficulty
                                }
                              </small>

                            </div>

                          )
                        )
                      }

                    </div>
                  )
            }

          </div>


          {/* RECENT ACTIVITY */}

          <div className="dashboard-panel">

            <div className="section-heading">

              <div>
                <h2>
                  Recent Activity
                </h2>

                <p>
                  Your latest quiz attempts.
                </p>
              </div>

            </div>


            {
              recent_activity.length === 0
                ? (
                    <p className="empty-text">
                      No quiz attempts yet.
                    </p>
                  )
                : (
                    <div className="activity-list">

                      {
                        recent_activity.map(
                          (attempt) => (

                            <div
                              className="activity-item"
                              key={
                                attempt
                                  .attempt_id
                              }
                            >

                              <div>

                                <strong>
                                  {
                                    attempt
                                      .topic_name
                                  }
                                </strong>

                                <span>
                                  {
                                    attempt
                                      .subject_name
                                  }
                                </span>

                              </div>


                              <strong>
                                {
                                  attempt
                                    .percentage
                                }%
                              </strong>

                            </div>

                          )
                        )
                      }

                    </div>
                  )
            }

          </div>

        </section>

      </main>

    </div>
  );
}


export default StudentDashboard;