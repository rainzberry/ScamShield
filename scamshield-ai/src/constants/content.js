/* Static informational content only (About / FAQ / Landing). No scan data lives here. */

export const PIPELINE = [
  { label: "Your submission", desc: "You submit an email, URL, text snippet or QR image through the scanner." },
  { label: "Flask REST API", desc: "The request is validated and authenticated by the backend." },
  { label: "Detection engine", desc: "Machine-learning models and rule checks extract features and score the content." },
  { label: "SQLite database", desc: "The scan and its explanation are stored so they appear in your history and dashboard." },
  { label: "Explained result", desc: "You receive a classification, risk score, confidence, indicators, evidence and a recommendation." },
];

export const ABOUT_TOPICS = [
  { title: "What ScamShield AI does", body: "ScamShield AI analyses emails, links, text messages and QR codes and classifies them as safe, spam, phishing, scam or malicious. Every result comes from the backend detection engine and includes the evidence behind it, so you can understand the decision rather than just trust a label." },
  { title: "Phishing", body: "Phishing is an attempt to trick you into revealing passwords, payment details or other sensitive information, usually by impersonating a trusted organisation. It often combines a lookalike sender, urgent wording and a link to a fake login page." },
  { title: "Spam", body: "Spam is unsolicited bulk messaging, typically promotional. It is usually a nuisance rather than a direct attack, but it can be used to deliver scams, so unexpected offers deserve caution." },
  { title: "Malicious content", body: "Malicious content is designed to harm your device or accounts, for example links that download malware or attachments that carry harmful code. It is treated as the most severe class." },
  { title: "QR scams (quishing)", body: "Quishing hides a malicious link inside a QR code, which people cannot read by eye. When you upload a QR image, the backend decodes it and analyses the payload. ScamShield never opens decoded links for you and the interface only displays them as plain text." },
  { title: "Risk score", body: "The risk score is a value from 0 to 100 describing how dangerous the content is estimated to be if you act on it. Higher means more potential harm." },
  { title: "Confidence", body: "Confidence describes how certain the model is about its classification. It is separate from risk: content can be high risk with only moderate confidence, so read both values together." },
  { title: "Explainable AI", body: "Results include the threat indicators that fired, the model features that influenced the prediction, rule-based checks and, for URLs, feature analysis. This evidence is provided by the backend; the interface does not invent explanations." },
  { title: "Limitations", body: "No automated system can guarantee that content is safe or unsafe. Models can make mistakes, especially on new attack styles. ScamShield is a decision aid, not a replacement for caution. Always verify sensitive requests through a trusted channel." },
  { title: "Gmail demo mode", body: "The Gmail page currently runs in Demo Gmail Mode. It shows sample messages only and no real Google account is accessed. Analysing a sample sends its text to the real detection backend, so the result is genuine, but the inbox itself is not." },
];

export const FAQ_ITEMS = [
  { q: "What is phishing?", a: "Phishing is a deceptive attempt to obtain sensitive information such as passwords or card numbers by impersonating a trusted sender." },
  { q: "What is the difference between spam and phishing?", a: "Spam is unwanted bulk messaging, usually advertising. Phishing is a deliberate attempt to steal credentials or money by impersonating someone you trust." },
  { q: "What is a QR scam (quishing)?", a: "Quishing places a malicious link behind a QR code. Because the destination is hidden, people scan it without checking. ScamShield decodes the QR image on the server and analyses the payload without opening it." },
  { q: "What does the risk score mean?", a: "A 0-100 estimate of how dangerous the content is if you act on it. Higher values indicate greater potential harm." },
  { q: "What does confidence mean?", a: "How certain the detection model is about its classification. Risk and confidence are different measures, so a result can have high risk and moderate confidence." },
  { q: "What is explainable AI here?", a: "Each result lists the indicators and evidence the backend found, plus model and rule features that influenced the outcome, so you can see why content was flagged." },
  { q: "Can ScamShield guarantee that something is safe?", a: "No. Detection is probabilistic and can be wrong. Treat results as guidance and use your own judgement for sensitive actions." },
  { q: "Does ScamShield open the links it finds?", a: "No. Links and decoded QR payloads are shown as plain text and are never opened or executed by the interface." },
  { q: "Is the Gmail connection real?", a: "Not currently. Gmail runs in Demo Gmail Mode with sample messages only. No real Google account is accessed." },
  { q: "What should I do after a high-risk result?", a: "Do not click links, open attachments or enter credentials. Report and delete the message, and verify through an official channel if you are unsure." },
];