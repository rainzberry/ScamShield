export function apiError(message) {
  const err = new Error(message);
  err.userMessage = message;
  return err;
}

/** Turns an Axios error into a short, safe, user-facing message. Never exposes stack traces. */
export function getErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  if (!error) return fallback;
  if (error.code === "ECONNABORTED") {
    return "The request timed out. The backend may be busy or unavailable.";
  }
  if (!error.response) {
    return "Backend unavailable. Check that the Flask server is running and the API URL is correct.";
  }
  const { status, data } = error.response;
  let serverMsg = null;
  if (typeof data?.error === "string") serverMsg = data.error;
  else if (typeof data?.message === "string") serverMsg = data.message;
  else if (typeof data?.error?.message === "string") serverMsg = data.error.message;

  const safe =
    serverMsg && serverMsg.length <= 300 && !/traceback|File ".*", line/i.test(serverMsg) ? serverMsg : null;

  if (status === 401) return safe || "Authentication failed.";
  if (status === 413) return "The uploaded file is too large.";
  if (status === 415) return "Invalid file. Upload a PNG, JPG or WebP image.";
  if (status === 503) return safe || "Model unavailable. The detection engine is not ready yet.";
  if (status >= 500) return safe || "The server could not complete the request. Please try again.";
  return safe || fallback;
}