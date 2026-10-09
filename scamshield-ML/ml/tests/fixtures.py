"""TEST FIXTURES ONLY - tiny hand-written samples used to exercise code paths in unit tests.
They are never used to train the real model."""
import pandas as pd

from ml.preprocessing.text_cleaning import clean_text

TEXT_SAFE = [
    "Hi team, attached is the agenda for Thursday's project meeting. Please review the notes before we meet.",
    "Thanks for your help with the quarterly report. Let me know if you need anything else from my side.",
    "Reminder: the library book you borrowed is due next week. You can renew it at the front desk.",
    "Lunch at one o'clock tomorrow? The new cafe near the office has a good menu.",
    "Here are the minutes from today's standup. Action items are listed at the bottom of the document.",
    "Your order has shipped and should arrive on Friday. Tracking details are available in your account.",
    "Can we move our one on one to Wednesday afternoon? I have a conflict with the design review.",
    "Great seeing you at the conference. I will send over the slides from my talk later this week.",
    "The maintenance window for the staging server is scheduled for Saturday night. No action is required.",
    "Please find the draft of the lab report attached. Comments and corrections are very welcome.",
    "Happy birthday! Hope you have a wonderful day with family and friends.",
    "The course schedule for next semester has been posted on the department notice board.",
]
TEXT_BAD = [
    "URGENT: Your account will be suspended within 24 hours. Verify your password now to avoid closure.",
    "Congratulations, you have won the lottery prize. Claim your reward by sending the processing fee today.",
    "Dear beneficiary, I am the late husband's lawyer and need your help to transfer 15 million dollars. Strictly confidential.",
    "Final notice: confirm your bank details and one time password immediately or your account will be locked.",
    "Buy now cheap viagra no prescription limited time discount click here for the lowest price",
    "Your PayPal account has been limited. Log in to verify your identity and restore access immediately.",
    "You are the lucky winner of a free iPhone. Claim your prize now, buy gift cards to cover the shipping fee.",
    "Security alert: unusual sign in detected. Confirm your credentials at the secure link below within 24 hours.",
    "Make money online fast, work from home, 100% guaranteed income. Order now and get a special offer.",
    "Your mailbox is full. Update your email password immediately to avoid losing important messages.",
    "I am a foreign partner with an unclaimed inheritance and need a trusted person to release the funds.",
    "Invoice overdue. Download the attached document and enter your login details to view payment instructions.",
]
URL_BENIGN = [
    "https://www.wikipedia.org/wiki/Machine_learning", "https://github.com/pallets/flask",
    "https://www.python.org/downloads/", "https://docs.python.org/3/library/re.html",
    "https://stackoverflow.com/questions/11227809", "https://www.bbc.com/news/technology",
    "https://www.nytimes.com/section/science", "https://en.wikipedia.org/wiki/Phishing",
    "https://www.mozilla.org/en-US/firefox/new/", "https://scikit-learn.org/stable/modules/ensemble.html",
    "https://www.coursera.org/learn/machine-learning", "https://www.paypal.com/in/home",
]
URL_BAD = [
    "http://192.168.4.20/paypal/login.php?session=ab12", "http://paypa1-secure-login.xyz/verify/account",
    "http://secure-update.amazon.com.account-check.top/signin", "https://bit.ly/3xYzAbC",
    "http://login-microsoft-verify.tk/office365/password", "http://xn--pple-43d.com/appleid/verify",
    "http://user@malicious-host.click/bank/login", "https://netflix-billing-update.icu/payment/confirm?id=88271",
    "http://203.0.113.9:8080/wallet/unlock", "http://g00gle-account-recovery.cyou/signin?continue=%2F%2Fmail",
    "https://amazon-prime-refund.work/claim/reward/verify", "http://hdfc-kyc-update.top/netbanking/login",
]

TINY_TEXT_PARAMS = {"word_min_df": 1, "char_min_df": 1, "c_grid": [1.0, 10.0]}
TINY_URL_PARAMS = {"n_estimators": 25, "grid": [{"max_depth": None, "min_samples_leaf": 1}],
                   "perm_sample": 50, "perm_repeats": 2}


def make_frames():
    def text_df(safe, bad):
        return pd.DataFrame({"text_clean": [clean_text(t) for t in safe + bad],
                             "label": [0] * len(safe) + [1] * len(bad)})

    def url_df(ben, bad):
        return pd.DataFrame({"url": ben + bad, "label": [0] * len(ben) + [1] * len(bad)})

    return (text_df(TEXT_SAFE[:9], TEXT_BAD[:9]), text_df(TEXT_SAFE[9:], TEXT_BAD[9:]),
            url_df(URL_BENIGN[:9], URL_BAD[:9]), url_df(URL_BENIGN[9:], URL_BAD[9:]))