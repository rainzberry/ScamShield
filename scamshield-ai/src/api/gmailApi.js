import { DEMO_INBOX } from "../constants/demoInbox";
import { apiError } from "../utils/errors";

/* Switch to "oauth" once the backend implements real Gmail OAuth.
   The Gmail page only talks to this module, so the UI does not need redesigning. */
export const GMAIL_MODE = "demo";

export async function listInbox() {
  if (GMAIL_MODE === "demo") {
    return { mode: "demo", messages: DEMO_INBOX };
  }
  throw apiError("Real Gmail OAuth is not supported by the backend yet.");
}