import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  apiRequest,
} from "../api/api";


function StudentRegister() {
  const navigate = useNavigate();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [school, setSchool] =
    useState("");

  const [
    preferredLanguage,
    setPreferredLanguage,
  ] = useState("English");

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    const cleanEmail =
      email.trim().toLowerCase();

    if (!cleanEmail) {
      setError(
        "Please enter your email address."
      );

      return;
    }

    if (!cleanEmail.includes("@")) {
      setError(
        "Please enter a valid email address."
      );

      return;
    }

    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );

      return;
    }

    if (
      password !== confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );

      return;
    }

    if (!school.trim()) {
      setError(
        "Please enter your school name."
      );

      return;
    }

    try {
      setLoading(true);

      await apiRequest(
        "/auth/register/",
        {
          method: "POST",

          body: {
            username: cleanEmail,
            email: cleanEmail,
            password,
            school: school.trim(),

            preferred_language:
              preferredLanguage,
          },
        }
      );

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate(
          "/student/login",
          {
            state: {
              registeredEmail:
                cleanEmail,
            },
          }
        );
      }, 1200);

    } catch (err) {
      setError(
        err.message ||
        "Unable to create account."
      );

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
            <h2>
              Adaptive Learning
            </h2>

            <span>
              KSEAB SSLC Class 10
            </span>
          </div>

        </div>


        <div className="login-message">

          <span className="welcome-badge">
            CREATE YOUR ACCOUNT
          </span>

          <h1>
            Start learning
            <span> smarter.</span>
          </h1>

          <p>
            Create your student account,
            choose your subjects and follow
            a personalized learning path.
          </p>


          <div className="feature-list">

            <div className="feature-item">
              <div className="feature-check">
                ✓
              </div>

              Karnataka SSLC curriculum
            </div>


            <div className="feature-item">
              <div className="feature-check">
                ✓
              </div>

              Adaptive quizzes based on mastery
            </div>


            <div className="feature-item">
              <div className="feature-check">
                ✓
              </div>

              Personalized recommendations
            </div>

          </div>

        </div>

      </div>


      <div className="login-right">

        <div className="login-card">

          <div className="login-card-heading">

            <h2>
              Create Student Account
            </h2>

            <p>
              Register to start your
              personalized learning journey.
            </p>

          </div>


          <form
            onSubmit={handleSubmit}
          >

            <div className="form-group">

              <label>
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value
                  )
                }
                placeholder="student@gmail.com"
                autoComplete="email"
              />

            </div>


            <div className="form-group">

              <label>
                School Name
              </label>

              <input
                type="text"
                value={school}
                onChange={(event) =>
                  setSchool(
                    event.target.value
                  )
                }
                placeholder="Enter your school"
              />

            </div>


            <div className="form-group">

              <label>
                Preferred Language
              </label>

              <select
                value={
                  preferredLanguage
                }
                onChange={(event) =>
                  setPreferredLanguage(
                    event.target.value
                  )
                }
              >

                <option value="English">
                  English
                </option>

                <option value="Kannada">
                  Kannada
                </option>

                <option value="Hindi">
                  Hindi
                </option>

              </select>

            </div>


            <div className="form-group">

              <label>
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value
                  )
                }
                placeholder="Create a password"
                autoComplete="new-password"
              />

            </div>


            <div className="form-group">

              <label>
                Confirm Password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(
                    event.target.value
                  )
                }
                placeholder="Enter password again"
                autoComplete="new-password"
              />

            </div>


            {error && (
              <div className="login-error">
                {error}
              </div>
            )}


            {success && (
              <div className="register-success">
                {success}
              </div>
            )}


            <button
              className="login-button"
              type="submit"
              disabled={loading}
            >

              {
                loading
                  ? "Creating account..."
                  : "Create Account"
              }

            </button>

          </form>


          <div className="account-link">

            Already have an account?

            <Link
              to="/student/login"
            >
              Sign In
            </Link>

          </div>

        </div>

      </div>

    </div>
  );
}


export default StudentRegister;