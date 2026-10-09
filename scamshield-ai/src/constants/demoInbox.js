/* DEMO ONLY. These are sample INPUTS (not results). Domains use the reserved ".example" TLD.
   When the user presses Analyze, the text is sent to POST /api/analyze/email and the real
   backend produces the result. */
export const DEMO_INBOX = [
  {
    id: "demo-1",
    from: "security@paypa1-support.example",
    subject: "URGENT: Verify your account now",
    snippet: "Your account will be suspended in 24 hours unless you verify...",
    body: "Your account will be suspended in 24 hours unless you verify your information. Click the link below to confirm your identity and password.",
    url: "https://paypa1-support.example/verify",
  },
  {
    id: "demo-2",
    from: "billing@invoice-secure-payments.example",
    subject: "Overdue invoice attached",
    snippet: "Your invoice is overdue. Open the attached file immediately...",
    body: "Your invoice is overdue. Open the attached file immediately to avoid legal action and service interruption.",
    url: "",
  },
  {
    id: "demo-3",
    from: "noreply@university.example",
    subject: "Your library book is due on Friday",
    snippet: "A friendly reminder that your borrowed item is due...",
    body: "Hello, this is a reminder that your borrowed item is due on Friday. You can renew it from the library page.",
    url: "",
  },
  {
    id: "demo-4",
    from: "deals@mega-savings-now.example",
    subject: "You have won a $500 gift card",
    snippet: "Congratulations! You were randomly selected to receive...",
    body: "Congratulations! You were randomly selected to receive a $500 gift card. Claim your prize before it expires.",
    url: "https://mega-savings-now.example/claim",
  },
  {
    id: "demo-5",
    from: "hr@company-internal-portal.example",
    subject: "Update your payroll direct deposit details",
    snippet: "Please confirm your direct deposit details within 24 hours...",
    body: "Our payroll system has been updated. Please confirm your direct deposit details within 24 hours to avoid a delay in payment.",
    url: "https://company-internal-portal.example/payroll",
  },
  {
    id: "demo-6",
    from: "team@project-tool.example",
    subject: "Weekly project summary",
    snippet: "Here is a summary of activity in your projects this week...",
    body: "Here is a summary of activity in your projects this week. No action is required.",
    url: "",
  },
];