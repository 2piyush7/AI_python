from __future__ import annotations

import argparse
import math
import re
import textwrap
from collections import Counter
from dataclasses import dataclass
from datetime import datetime


STOP_WORDS = {
    "a",
    "about",
    "after",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "been",
    "by",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "get",
    "give",
    "have",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "or",
    "please",
    "should",
    "tell",
    "that",
    "the",
    "their",
    "there",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "you",
}


SYNONYMS = {
    "admission": "admissions",
    "admit": "admissions",
    "apply": "application",
    "applying": "application",
    "fee": "fees",
    "payment": "fees",
    "scholarship": "scholarships",
    "exam": "exams",
    "test": "exams",
    "marks": "results",
    "mark": "results",
    "grade": "results",
    "grades": "results",
    "hallticket": "hall ticket",
    "admitcard": "admit card",
    "hostel": "hostels",
    "library": "library",
    "wifi": "wi-fi",
    "internet": "wi-fi",
    "cafeteria": "canteen",
    "food": "canteen",
    "bus": "transport",
    "medical": "health center",
    "doctor": "health center",
}


@dataclass(frozen=True)
class KnowledgeItem:
    category: str
    question: str
    answer: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class ChatResponse:
    answer: str
    category: str
    confidence: float
    suggested_questions: list[str]


KNOWLEDGE_BASE = [
    KnowledgeItem(
        category="Admissions",
        question="How do I apply for admission?",
        answer=(
            "You can apply through the online admissions portal. Create an account, "
            "choose your program, fill in personal and academic details, upload the "
            "required documents, pay the application fee, and submit the form before "
            "the deadline."
        ),
        keywords=("admissions", "application", "apply", "portal", "program"),
    ),
    KnowledgeItem(
        category="Admissions",
        question="Which documents are required for admission?",
        answer=(
            "Usually required documents include 10th and 12th mark sheets, transfer "
            "certificate, government ID, passport-size photo, entrance scorecard if "
            "applicable, caste or income certificate if claiming a reserved category "
            "or scholarship, and migration certificate for students from other boards."
        ),
        keywords=("documents", "certificate", "marksheet", "id", "photo"),
    ),
    KnowledgeItem(
        category="Admissions",
        question="What is the admission eligibility criteria?",
        answer=(
            "Eligibility depends on the course. For most undergraduate programs, "
            "students must have completed 10+2 or equivalent with the required "
            "subjects and minimum percentage. Entrance-test scores may be required "
            "for selected programs."
        ),
        keywords=("eligibility", "criteria", "percentage", "subjects", "qualification"),
    ),
    KnowledgeItem(
        category="Admissions",
        question="How can I check my admission status?",
        answer=(
            "Log in to the admissions portal with your registered email or application "
            "number. The dashboard shows whether your application is submitted, under "
            "review, shortlisted, selected, waitlisted, or rejected."
        ),
        keywords=("status", "shortlisted", "selected", "application", "dashboard"),
    ),
    KnowledgeItem(
        category="Admissions",
        question="Are scholarships available?",
        answer=(
            "Yes. The college may offer merit-based, need-based, sports, reserved "
            "category, and government scholarships. Students should submit scholarship "
            "forms with supporting documents before the announced deadline."
        ),
        keywords=("scholarships", "merit", "income", "financial", "aid"),
    ),
    KnowledgeItem(
        category="Admissions",
        question="How do I pay college fees?",
        answer=(
            "Fees can normally be paid online through the student portal using UPI, "
            "net banking, card, or challan where available. Keep the receipt or "
            "transaction ID for verification."
        ),
        keywords=("fees", "payment", "receipt", "upi", "challan"),
    ),
    KnowledgeItem(
        category="Exams",
        question="Where can I find the exam timetable?",
        answer=(
            "Exam timetables are published on the student portal and the examination "
            "notice board. Check your department, semester, subject code, date, time, "
            "and exam room carefully."
        ),
        keywords=("exams", "timetable", "schedule", "date", "room"),
    ),
    KnowledgeItem(
        category="Exams",
        question="How do I download my hall ticket or admit card?",
        answer=(
            "Open the student portal, go to the Examination section, select the current "
            "semester, and download your hall ticket or admit card. Clear pending fees "
            "or form issues first if the download option is locked."
        ),
        keywords=("hall ticket", "admit card", "download", "semester", "portal"),
    ),
    KnowledgeItem(
        category="Exams",
        question="What should I do if I miss an exam?",
        answer=(
            "Contact the examination cell and your department immediately. If the "
            "absence was due to a valid emergency, submit an application with proof. "
            "The examination cell will explain whether a re-exam, backlog, or special "
            "case process is available."
        ),
        keywords=("miss", "absent", "re-exam", "backlog", "emergency"),
    ),
    KnowledgeItem(
        category="Exams",
        question="How can I check exam results?",
        answer=(
            "Results are usually available in the student portal under Examination or "
            "Results. Enter your roll number or login credentials, select the semester, "
            "and download the grade sheet when it is published."
        ),
        keywords=("results", "marks", "grades", "roll", "semester"),
    ),
    KnowledgeItem(
        category="Exams",
        question="How do I apply for revaluation?",
        answer=(
            "After results are declared, eligible students can apply for revaluation "
            "through the examination portal or exam cell. Submit the subject details "
            "and pay the revaluation fee before the deadline."
        ),
        keywords=("revaluation", "recheck", "rechecking", "answer", "sheet"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="What are the library timings?",
        answer=(
            "The library is generally open on working days from 9:00 AM to 6:00 PM. "
            "During exams, extended hours may be announced by the library office."
        ),
        keywords=("library", "timings", "books", "study", "reading"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="Is hostel accommodation available?",
        answer=(
            "Hostel accommodation may be available for eligible students based on seat "
            "availability. Apply through the hostel office or student portal and submit "
            "ID proof, admission proof, and fee receipt."
        ),
        keywords=("hostels", "accommodation", "room", "warden", "mess"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="How do I access campus Wi-Fi?",
        answer=(
            "Students can request Wi-Fi access from the IT helpdesk. You will usually "
            "need your student ID and registered mobile number. Use your assigned "
            "credentials and follow the acceptable-use policy."
        ),
        keywords=("wi-fi", "internet", "network", "password", "it"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="What food facilities are available on campus?",
        answer=(
            "The campus canteen provides snacks, meals, and beverages during working "
            "hours. Hostel students may also have access to mess facilities according "
            "to the hostel schedule."
        ),
        keywords=("canteen", "food", "mess", "lunch", "snacks"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="Is transport facility available?",
        answer=(
            "College transport may be available on selected routes. Contact the "
            "transport office for route details, bus timings, fees, and seat availability."
        ),
        keywords=("transport", "bus", "route", "timings", "pickup"),
    ),
    KnowledgeItem(
        category="Campus Facilities",
        question="Where can I get medical help on campus?",
        answer=(
            "For minor health concerns or first aid, visit the campus health center. "
            "For emergencies, inform security, your department office, or the nearest "
            "faculty member immediately."
        ),
        keywords=("health center", "medical", "first aid", "emergency", "doctor"),
    ),
]


GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
THANKS = {"thanks", "thank you", "thx", "okay thanks", "ok thanks"}
GOODBYES = {"bye", "exit", "quit", "goodbye", "see you"}


def normalize_text(text: str) -> str:
    normalized = text.lower().replace("-", " ")
    normalized = re.sub(r"[^a-z0-9+\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    for source, target in SYNONYMS.items():
        normalized = re.sub(rf"\b{re.escape(source)}\b", target, normalized)

    return normalized


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = normalized.split()
    joined_tokens: list[str] = []
    index = 0

    while index < len(tokens):
        pair = " ".join(tokens[index : index + 2])
        if pair in {"hall ticket", "admit card", "health center"}:
            joined_tokens.append(pair)
            index += 2
            continue
        token = tokens[index]
        if token not in STOP_WORDS and len(token) > 1:
            joined_tokens.append(token)
        index += 1

    bigrams = [
        f"{joined_tokens[index]} {joined_tokens[index + 1]}"
        for index in range(len(joined_tokens) - 1)
    ]
    return joined_tokens + bigrams


def build_document(item: KnowledgeItem) -> str:
    return " ".join([item.category, item.question, item.answer, *item.keywords])


class StudentQueryChatbot:
    def __init__(self, knowledge_base: list[KnowledgeItem]) -> None:
        self.knowledge_base = knowledge_base
        self.documents = [tokenize(build_document(item)) for item in knowledge_base]
        self.idf = self._compute_idf(self.documents)
        self.vectors = [self._vectorize(document) for document in self.documents]

    def _compute_idf(self, documents: list[list[str]]) -> dict[str, float]:
        document_count = len(documents)
        document_frequencies: Counter[str] = Counter()

        for document in documents:
            document_frequencies.update(set(document))

        return {
            term: math.log((1 + document_count) / (1 + frequency)) + 1
            for term, frequency in document_frequencies.items()
        }

    def _vectorize(self, terms: list[str]) -> dict[str, float]:
        counts = Counter(terms)
        total = sum(counts.values()) or 1
        return {
            term: (count / total) * self.idf.get(term, 1.0)
            for term, count in counts.items()
        }

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        common_terms = set(left) & set(right)
        numerator = sum(left[term] * right[term] for term in common_terms)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))

        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _top_items(self, query: str, limit: int = 3) -> list[tuple[KnowledgeItem, float]]:
        query_vector = self._vectorize(tokenize(query))
        scored_items = [
            (item, self._cosine(query_vector, vector))
            for item, vector in zip(self.knowledge_base, self.vectors)
        ]
        scored_items.sort(key=lambda pair: pair[1], reverse=True)
        return scored_items[:limit]

    def _suggestions(self, category: str | None = None, limit: int = 3) -> list[str]:
        suggestions = [
            item.question
            for item in self.knowledge_base
            if category is None or item.category == category
        ]
        return suggestions[:limit]

    def answer(self, query: str) -> ChatResponse:
        normalized = normalize_text(query)

        if not normalized:
            return ChatResponse(
                answer="Please type your question about admissions, exams, or campus facilities.",
                category="General",
                confidence=0.0,
                suggested_questions=self._suggestions(),
            )

        if normalized in GREETINGS:
            return ChatResponse(
                answer=(
                    "Hello! I can help with admissions, exams, scholarships, fees, "
                    "hostels, library, Wi-Fi, transport, canteen, and medical facilities."
                ),
                category="General",
                confidence=1.0,
                suggested_questions=self._suggestions(),
            )

        if normalized in THANKS:
            return ChatResponse(
                answer="You are welcome. Ask me anytime you need student support information.",
                category="General",
                confidence=1.0,
                suggested_questions=[],
            )

        if normalized in GOODBYES:
            return ChatResponse(
                answer="Goodbye! Wishing you a smooth campus day.",
                category="General",
                confidence=1.0,
                suggested_questions=[],
            )

        top_items = self._top_items(query)
        best_item, best_score = top_items[0]

        if best_score < 0.035:
            return ChatResponse(
                answer=(
                    "I could not find a confident answer for that. Please contact the "
                    "student helpdesk or ask about admissions, exams, or campus facilities."
                ),
                category="Fallback",
                confidence=best_score,
                suggested_questions=self._suggestions(),
            )

        related = [
            item.question
            for item, score in top_items[1:]
            if score > 0.02 and item.category == best_item.category
        ]

        return ChatResponse(
            answer=best_item.answer,
            category=best_item.category,
            confidence=min(best_score * 4, 1.0),
            suggested_questions=related or self._suggestions(best_item.category),
        )


def format_response(response: ChatResponse) -> str:
    confidence = f"{response.confidence * 100:.0f}%"
    output = [
        f"[{response.category} | confidence: {confidence}]",
        textwrap.fill(response.answer, width=88),
    ]

    if response.suggested_questions:
        output.append("Related questions:")
        output.extend(f"  - {question}" for question in response.suggested_questions)

    return "\n".join(output)


def print_welcome() -> None:
    print("AI-Powered Student Helpdesk Chatbot")
    print("=" * 72)
    print("Ask about admissions, exams, scholarships, fees, hostels, library, Wi-Fi,")
    print("transport, canteen, or medical facilities. Type 'exit' to quit.")
    print("=" * 72)


def interactive_chat() -> None:
    chatbot = StudentQueryChatbot(KNOWLEDGE_BASE)
    print_welcome()

    while True:
        try:
            query = input("\nStudent: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break

        response = chatbot.answer(query)
        print("\nBot:")
        print(format_response(response))

        if normalize_text(query) in GOODBYES:
            break


def run_demo() -> None:
    chatbot = StudentQueryChatbot(KNOWLEDGE_BASE)
    demo_questions = [
        "How can I apply for admission?",
        "Where is my exam timetable?",
        "How do I download hall ticket?",
        "Is hostel available?",
        "How can I use campus wifi?",
        "Where can I get medical help?",
    ]

    print("Student Helpdesk Chatbot Demo")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    for question in demo_questions:
        print(f"\nStudent: {question}")
        print("Bot:")
        print(format_response(chatbot.answer(question)))


def list_topics() -> None:
    categories: dict[str, list[str]] = {}
    for item in KNOWLEDGE_BASE:
        categories.setdefault(item.category, []).append(item.question)

    print("Available Chatbot Topics")
    print("=" * 72)
    for category, questions in categories.items():
        print(f"\n{category}")
        for question in questions:
            print(f"  - {question}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-powered chatbot for student admissions, exam, and campus queries."
    )
    parser.add_argument("--demo", action="store_true", help="Run sample questions.")
    parser.add_argument("--topics", action="store_true", help="Show supported questions.")
    parser.add_argument("--ask", help="Ask one question and print the answer.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chatbot = StudentQueryChatbot(KNOWLEDGE_BASE)

    if args.topics:
        list_topics()
        return

    if args.demo:
        run_demo()
        return

    if args.ask:
        print(format_response(chatbot.answer(args.ask)))
        return

    interactive_chat()


if __name__ == "__main__":
    main()
