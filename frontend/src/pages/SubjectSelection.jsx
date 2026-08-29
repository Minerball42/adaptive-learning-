import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  apiRequest,
  getStudentToken,
} from "../api/api";


function SubjectSelection() {
  const navigate = useNavigate();

  const [data, setData] = useState(null);

  const [firstLanguage, setFirstLanguage] =
    useState("");

  const [secondLanguage, setSecondLanguage] =
    useState("");

  const [thirdLanguage, setThirdLanguage] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {
    loadSubjects();
  }, []);


  async function loadSubjects() {
    const token = getStudentToken();

    if (!token) {
      navigate("/student/login");
      return;
    }

    try {
      const response = await apiRequest(
        "/auth/subjects/",
        {
          token,
        }
      );

      setData(response);

      const selected =
        response.selected_subjects || [];

      const first = selected.find(
        (subject) =>
          subject.subject_type ===
          "first_language"
      );

      const second = selected.find(
        (subject) =>
          subject.subject_type ===
          "second_language"
      );

      const third = selected.find(
        (subject) =>
          subject.subject_type ===
          "third_language"
      );

      if (first) {
        setFirstLanguage(
          String(first.id)
        );
      }

      if (second) {
        setSecondLanguage(
          String(second.id)
        );
      }

      if (third) {
        setThirdLanguage(
          String(third.id)
        );
      }

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  async function saveSubjects(event) {
    event.preventDefault();

    if (
      !firstLanguage ||
      !secondLanguage ||
      !thirdLanguage
    ) {
      setError(
        "Please select all three languages."
      );

      return;
    }

    try {
      setSaving(true);
      setError("");

      await apiRequest(
        "/auth/subjects/",
        {
          method: "POST",

          token: getStudentToken(),

          body: {
            first_language:
              Number(firstLanguage),

            second_language:
              Number(secondLanguage),

            third_language:
              Number(thirdLanguage),

            optional_subjects: [],
          },
        }
      );

      navigate(
        "/student/dashboard"
      );

    } catch (err) {
      setError(err.message);

    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading subjects...
      </div>
    );
  }


  if (!data) {
    return (
      <div className="dashboard-error-page">
        <h2>
          Unable to load subjects
        </h2>

        <p>{error}</p>
      </div>
    );
  }


  return (
    <div className="subject-selection-page">

      <div className="subject-selection-card">

        <div className="selection-heading">

          <span>
            KSEAB SSLC CLASS 10
          </span>

          <h1>
            Choose Your Subjects
          </h1>

          <p>
            Core subjects are included
            automatically. Select your
            three language subjects.
          </p>

        </div>


        <div className="core-subject-box">

          <h3>
            Core Subjects
          </h3>

          <div className="core-subject-list">

            {data.core_subjects.map(
              (subject) => (
                <div
                  className="core-subject-chip"
                  key={subject.id}
                >
                  ✓ {subject.name}
                </div>
              )
            )}

          </div>

        </div>


        <form
          onSubmit={saveSubjects}
        >

          <div className="form-group">

            <label>
              First Language
            </label>

            <select
              value={firstLanguage}
              onChange={(event) =>
                setFirstLanguage(
                  event.target.value
                )
              }
            >

              <option value="">
                Select first language
              </option>

              {data.first_languages.map(
                (subject) => (
                  <option
                    key={subject.id}
                    value={subject.id}
                  >
                    {subject.name}
                  </option>
                )
              )}

            </select>

          </div>


          <div className="form-group">

            <label>
              Second Language
            </label>

            <select
              value={secondLanguage}
              onChange={(event) =>
                setSecondLanguage(
                  event.target.value
                )
              }
            >

              <option value="">
                Select second language
              </option>

              {data.second_languages.map(
                (subject) => (
                  <option
                    key={subject.id}
                    value={subject.id}
                  >
                    {subject.name}
                  </option>
                )
              )}

            </select>

          </div>


          <div className="form-group">

            <label>
              Third Language
            </label>

            <select
              value={thirdLanguage}
              onChange={(event) =>
                setThirdLanguage(
                  event.target.value
                )
              }
            >

              <option value="">
                Select third language
              </option>

              {data.third_languages.map(
                (subject) => (
                  <option
                    key={subject.id}
                    value={subject.id}
                  >
                    {subject.name}
                  </option>
                )
              )}

            </select>

          </div>


          {error && (
            <div className="login-error">
              {error}
            </div>
          )}


          <button
            className="login-button"
            disabled={saving}
          >
            {
              saving
                ? "Saving..."
                : "Save Subjects"
            }
          </button>

        </form>

      </div>

    </div>
  );
}


export default SubjectSelection;