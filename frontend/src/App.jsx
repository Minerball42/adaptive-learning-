import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";


import StudentLogin
  from "./pages/StudentLogin";

import StudentRegister
  from "./pages/StudentRegister";

import StudentDashboard
  from "./pages/StudentDashboard";

import SubjectSelection
  from "./pages/SubjectSelection";

import SubjectChapters
  from "./pages/SubjectChapters";

import ChapterTopics
  from "./pages/ChapterTopics";

import TopicLesson
  from "./pages/TopicLesson";

import AdaptiveQuiz
  from "./pages/AdaptiveQuiz";


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={
            <Navigate
              to="/student/login"
              replace
            />
          }
        />


        <Route
          path="/student/register"
          element={
            <StudentRegister />
          }
        />


        <Route
          path="/student/login"
          element={
            <StudentLogin />
          }
        />


        <Route
          path="/student/subjects/select"
          element={
            <SubjectSelection />
          }
        />


        <Route
          path="/student/dashboard"
          element={
            <StudentDashboard />
          }
        />


        <Route
          path="/student/subject/:subjectId/chapters"
          element={
            <SubjectChapters />
          }
        />


        <Route
          path="/student/chapter/:chapterId/topics"
          element={
            <ChapterTopics />
          }
        />


        <Route
          path="/student/topic/:topicId"
          element={
            <TopicLesson />
          }
        />


        <Route
          path="/student/topic/:topicId/quiz"
          element={
            <AdaptiveQuiz />
          }
        />


        <Route
          path="*"
          element={
            <Navigate
              to="/student/dashboard"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;