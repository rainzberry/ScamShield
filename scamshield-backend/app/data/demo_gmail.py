"""SAMPLE INPUTS for the clearly-labelled Demo Gmail Mode.

These are NOT real Gmail messages and carry NO verdicts. They are just realistic text the
user can submit to POST /api/analyze/email, so every result still comes from the real ML
engine. Domains are fictional and are never contacted.
"""

DEMO_LABEL = "DEMO MODE - sample messages, not connected to a real Gmail account"
DEMO_ADDRESS = "demo.user@scamshield.local"

DEMO_MESSAGES = [
    {
        "id": "demo-001",
        "sender": "registrar@university-example.edu",
        "subject": "Semester timetable published",
        "date": "2026-10-05T09:15:00Z",
        "body": ("Hello,\n\nThe timetable for the new semester is now available on the student "
                 "portal. Please review your registered courses before Friday and contact the "
                 "registrar's office if anything looks wrong.\n\nRegards,\nOffice of the Registrar"),
        "url": None,
    },
    {
        "id": "demo-002",
        "sender": "security-alert@secure-bank-verify-login.top",
        "subject": "URGENT: Your account will be suspended",
        "date": "2026-10-06T02:41:00Z",
        "body": ("Dear customer,\n\nWe detected unusual activity. Your account will be suspended "
                 "within 24 hours unless you verify your identity immediately.\n\n"
                 "Verify now: http://secure-bank-verify-login.top/kyc\n\nBank Security Team"),
        "url": "http://secure-bank-verify-login.top/kyc",
    },
    {
        "id": "demo-003",
        "sender": "rewards@mega-prize-center.xyz",
        "subject": "Congratulations! You have won a free prize",
        "date": "2026-10-06T14:20:00Z",
        "body": ("You have been selected to receive a FREE gift worth Rs. 50,000. Claim your "
                 "reward now - limited offer, expires tonight! Reply with your full name and "
                 "phone number."),
        "url": None,
    },
    {
        "id": "demo-004",
        "sender": "team@project-example.org",
        "subject": "Meeting notes - Thursday sync",
        "date": "2026-10-07T11:00:00Z",
        "body": ("Hi all,\n\nNotes from today's sync are in the shared folder. Action items: "
                 "finalise the dataset, review the draft report, and book the demo slot."),
        "url": None,
    },
    {
        "id": "demo-005",
        "sender": "delivery@parcel-redelivery-info.top",
        "subject": "Package on hold - pay a small fee",
        "date": "2026-10-07T18:05:00Z",
        "body": ("Your parcel could not be delivered. Pay a redelivery fee of Rs. 25 within 12 "
                 "hours or it will be returned: http://parcel-redelivery-info.top/pay"),
        "url": "http://parcel-redelivery-info.top/pay",
    },
]
