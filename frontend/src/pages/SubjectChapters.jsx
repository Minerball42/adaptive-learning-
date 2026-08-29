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


function SubjectChapters() {
  const navigate = useNavigate();

  const { subjectId } = useParams();

  const [searchParams] = useSearchParams();

  const subjectName =
    searchParams.get("name") || "Subject";

  const [chapters, setChapters] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    loadChapters();
  }, [subjectId]);


  async function loadChapters() {
    const token = getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await apiRequest(
        `/courses/chapters/?subject=${subjectId}`,
        {
          token,
        }
      );

      setChapters(
        normalizeList(response)
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
        Loading chapters...
      </div>
    );
  }


  return (
    <div className="content-page">

      <div className="content-page-header">

        <button
          className="back-button"
          onClick={() =>
            navigate("/student/dashboard")
          }
        >
          ← Dashboard
        </button>

        <p className="dashboard-label">
          SUBJECT
        </p>

        <h1>{subjectName}</h1>

        <p>
          Select any chapter to view
          its topics.
        </p>

      </div>


      {error && (
        <div className="login-error">
          {error}
        </div>
      )}


      <div className="chapter-grid">

        {chapters.map((chapter) => (

          <button
            key={chapter.id}
            className="chapter-card"

            onClick={() =>
              navigate(
                `/student/chapter/${chapter.id}/topics` +
                `?subject=${encodeURIComponent(subjectName)}` +
                `&chapter=${encodeURIComponent(chapter.name)}`
              )
            }
          >

            <span className="chapter-number">
              Chapter {chapter.chapter_number}
            </span>

            <h3>
              {chapter.name}
            </h3>

            <p>
              Explore topics →
            </p>

          </button>

        ))}

      </div>

    </div>
  );
}


export default SubjectChapters;