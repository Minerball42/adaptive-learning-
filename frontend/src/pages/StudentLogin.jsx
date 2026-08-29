import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  apiRequest,
  setStudentToken,
} from "../api/api";


function StudentLogin() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (!username.trim() || !password) {
      setError("Please enter your username and password.");
      return;
    }

    try {
      setLoading(true);

      const data = await apiRequest(
         "/auth/login/",
        {
          method: "POST",

          body: {
            username: username.trim(),
            password,
          },
        }
      );

      setStudentToken(data.token);

      localStorage.setItem(
        "student_profile",
        JSON.stringify(data.student)
      );

      navigate("/student/dashboard");

    } catch (err) {
      setError(err.message);

    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="login-page">

      <div className="login-left">

        <div className="brand">
          <div className="brand-icon">
            AL
          </div>

          <div>
            <h2>Adaptive Learning</h2>
            <span>KSEAB SSLC Class 10</span>
          </div>
        </div>

        <div className="login-message">
          <span className="welcome-badge">
            PERSONALIZED LEARNING
          </span>

          <h1>
            Learn at your own
            <span> pace.</span>
          </h1>

          <p>
            Study lessons, take adaptive quizzes,
            track your mastery, and receive
            personalized recommendations.
          </p>

          <div className="feature-list">

            <div className="feature-item">
              <div className="feature-check">✓</div>
              Adaptive Easy → Medium → Hard quizzes
            </div>

            <div className="feature-item">
              <div className="feature-check">✓</div>
              Personalized learning path
            </div>

            <div className="feature-item">
              <div className="feature-check">✓</div>
              Real-time mastery and progress tracking
            </div>

          </div>
        </div>

      </div>


      <div className="login-right">

        <div className="login-card">

          <div className="login-card-heading">
            <h2>Student Login</h2>

            <p>
              Welcome back! Continue your
              learning journey.
            </p>
          </div>


          <form onSubmit={handleSubmit}>

            <div className="form-group">
              <label>Username</label>

              <input
                type="text"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="Enter your username"
                autoComplete="username"
              />
            </div>


            <div className="form-group">
              <label>Password</label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>


            {error && (
              <div className="login-error">
                {error}
              </div>
            )}


            <button
              className="login-button"
              type="submit"
              disabled={loading}
            >
              {
                loading
                  ? "Signing in..."
                  : "Sign In"
              }
            </button>

          </form>


          <div className="login-demo-note">
            <strong>Adaptive Learning Platform</strong>
            <span>
              Karnataka SSLC Class 10
            </span>
          </div>

        </div>

      </div>

    </div>
  );
}


export default StudentLogin;