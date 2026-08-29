import { useEffect, useState } from "react";

import {
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";

import {
  apiRequest,
  getStudentToken,
  normalizeList,
} from "../api/api";


function ChapterTopics() {
  const navigate = useNavigate();

  const { chapterId } = useParams();

  const [searchParams] = useSearchParams();

  const subjectName =
    searchParams.get("subject") || "Subject";

  const chapterName =
    searchParams.get("chapter") || "Chapter";

  const [topics, setTopics] = useState([]);

  const [loading, setLoading] = useState(true);

  const [progressLoading, setProgressLoading] =
    useState(false);

  const [error, setError] = useState("");


  useEffect(() => {
    loadTopics();
  }, [chapterId]);


  async function loadTopics() {
    const token = getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    const cacheKey =
      `chapter_topics_${chapterId}`;

    /*
     * =====================================================
     * SHOW CACHE IMMEDIATELY
     * =====================================================
     */

    const cached =
      sessionStorage.getItem(cacheKey);

    if (cached) {
      try {
        const cachedTopics =
          JSON.parse(cached);

        if (Array.isArray(cachedTopics)) {
          setTopics(cachedTopics);
          setLoading(false);
        }
      } catch {
        sessionStorage.removeItem(
          cacheKey
        );
      }
    }


    /*
     * =====================================================
     * LOAD ONLY THIS CHAPTER
     * =====================================================
     */

    try {
      setError("");

      const topicResponse =
        await apiRequest(
          `/courses/topics/?chapter=${chapterId}`,
          {
            token,
          }
        );

      const topicList =
        normalizeList(topicResponse);


      /*
       * Show topics IMMEDIATELY.
       *
       * We do not wait for all 370-topic progress
       * calculations before rendering.
       */

      const immediateTopics =
        topicList.map(
          (topic) => ({
            ...topic,

            unlocked: true,

            status: "available",

            level: "not_started",

            mastery_score: 0,

            previous_topic: null,

            progress_checked: false,
          })
        );


      setTopics(immediateTopics);

      setLoading(false);


      sessionStorage.setItem(
        cacheKey,
        JSON.stringify(
          immediateTopics
        )
      );


      /*
       * =====================================================
       * LOAD PROGRESS IN BACKGROUND
       * =====================================================
       */

      loadProgressInBackground(
        immediateTopics,
        token,
        cacheKey
      );

    } catch (err) {
      setLoading(false);

      setError(
        err.message
      );
    }
  }


  async function loadProgressInBackground(
    currentTopics,
    token,
    cacheKey
  ) {
    try {
      setProgressLoading(true);


      /*
       * Reuse recently fetched learning path
       * during this browser session.
       */

      const progressCache =
        sessionStorage.getItem(
          "student_learning_path"
        );

      const progressTime =
        Number(
          sessionStorage.getItem(
            "student_learning_path_time"
          )
        );


      const now = Date.now();

      let pathResponse = null;


      /*
       * Cache remains valid for 2 minutes.
       */

      if (
        progressCache &&
        progressTime &&
        now - progressTime < 120000
      ) {
        pathResponse =
          JSON.parse(
            progressCache
          );
      } else {
        pathResponse =
          await apiRequest(
            "/progress/learning-path/",
            {
              token,
            }
          );


        sessionStorage.setItem(
          "student_learning_path",
          JSON.stringify(
            pathResponse
          )
        );


        sessionStorage.setItem(
          "student_learning_path_time",
          String(now)
        );
      }


      const progressTopics =
        pathResponse?.topics || [];


      const progressMap =
        new Map(
          progressTopics.map(
            (item) => [
              item.topic_id,
              item,
            ]
          )
        );


      const merged =
        currentTopics.map(
          (topic) => {

            const progress =
              progressMap.get(
                topic.id
              );


            if (!progress) {
              return {
                ...topic,

                progress_checked:
                  true,
              };
            }


            return {
              ...topic,

              unlocked:
                progress.unlocked,

              status:
                progress.status,

              level:
                progress.level,

              mastery_score:
                progress.mastery_score,

              previous_topic:
                progress.previous_topic,

              progress_checked:
                true,
            };
          }
        );


      setTopics(merged);


      sessionStorage.setItem(
        cacheKey,
        JSON.stringify(merged)
      );

    } catch (err) {
      /*
       * Topics remain usable even if
       * progress loading fails.
       */

      console.error(
        "Progress loading failed:",
        err
      );

    } finally {
      setProgressLoading(false);
    }
  }


  function openTopic(topic) {
    /*
     * Once backend progress has confirmed
     * that a topic is locked, block it.
     */

    if (
      topic.progress_checked &&
      !topic.unlocked
    ) {
      return;
    }


    navigate(
      `/student/topic/${topic.id}`
    );
  }


  if (loading) {
    return (
      <div className="page-loader">
        <div className="loader-spinner" />
        <span>
          Loading topics...
        </span>
      </div>
    );
  }


  return (
    <div className="content-page">

      <div className="page-container">

        <div className="content-page-header">

          <button
            className="back-button"
            onClick={() =>
              navigate(-1)
            }
          >
            ← Back to Chapters
          </button>


          <div className="page-eyebrow">
            {subjectName}
          </div>


          <div className="page-title-row">

            <div>
              <h1>
                {chapterName}
              </h1>

              <p>
                Learn the topics in order
                and improve your mastery.
              </p>
            </div>


            {progressLoading && (
              <span className="sync-badge">
                Updating progress...
              </span>
            )}

          </div>

        </div>


        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}


        <div className="topic-list">

          {topics.map(
            (topic, index) => {

              const isLocked =
                topic.progress_checked &&
                !topic.unlocked;


              const completed =
                topic.level === "strong";


              return (
                <button
                  key={topic.id}

                  className={
                    `topic-card ${
                      isLocked
                        ? "topic-locked"
                        : "topic-unlocked"
                    }`
                  }

                  disabled={isLocked}

                  onClick={() =>
                    openTopic(topic)
                  }
                >

                  <div
                    className={
                      `topic-index ${
                        completed
                          ? "topic-complete-index"
                          : ""
                      }`
                    }
                  >
                    {
                      completed
                        ? "✓"
                        : index + 1
                    }
                  </div>


                  <div className="topic-main">

                    <div className="topic-title-row">

                      <h3>
                        {topic.name}
                      </h3>


                      <span
                        className={
                          `status-pill ${
                            completed
                              ? "status-complete"
                              : isLocked
                                ? "status-locked"
                                : "status-open"
                          }`
                        }
                      >

                        {
                          completed
                            ? "Completed"
                            : isLocked
                              ? "Locked"
                              : "Available"
                        }

                      </span>

                    </div>


                    <div className="topic-meta">

                      <span>
                        Level:
                        {" "}
                        <strong>
                          {
                            topic.level
                              ?.replaceAll(
                                "_",
                                " "
                              )
                          }
                        </strong>
                      </span>


                      <span>
                        Mastery:
                        {" "}
                        <strong>
                          {
                            topic.mastery_score
                          }%
                        </strong>
                      </span>

                    </div>


                    {
                      isLocked &&
                      topic.previous_topic && (
                        <div className="lock-note">

                          Complete
                          {" "}

                          <strong>
                            {
                              topic
                                .previous_topic
                                .name
                            }
                          </strong>

                          {" "}to unlock this topic.

                        </div>
                      )
                    }

                  </div>


                  <div className="topic-arrow">
                    {
                      isLocked
                        ? "🔒"
                        : "→"
                    }
                  </div>

                </button>
              );

            }
          )}

        </div>


        {
          topics.length === 0 &&
          !error && (
            <div className="empty-state">
              No topics are available
              in this chapter.
            </div>
          )
        }

      </div>

    </div>
  );
}


export default ChapterTopics;