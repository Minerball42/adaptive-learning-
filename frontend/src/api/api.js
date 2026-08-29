const API_BASE = "/api";


export function getStudentToken() {
  return localStorage.getItem("student_token");
}


export function setStudentToken(token) {
  localStorage.setItem("student_token", token);
}


export function removeStudentToken() {
  localStorage.removeItem("student_token");
}


export function getTeacherToken() {
  return localStorage.getItem("teacher_token");
}


export function setTeacherToken(token) {
  localStorage.setItem("teacher_token", token);
}


export function removeTeacherToken() {
  localStorage.removeItem("teacher_token");
}


export function normalizeList(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  if (Array.isArray(data?.value)) {
    return data.value;
  }

  return [];
}


export async function apiRequest(
  path,
  {
    method = "GET",
    body = null,
    token = null,
  } = {}
) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const options = {
    method,
    headers,
  };

  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(
    `${API_BASE}${path}`,
    options
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.error ||
      data?.message ||
      data?.detail ||
      "Something went wrong."
    );
  }

  return data;
}