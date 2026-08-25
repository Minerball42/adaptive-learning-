from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Chapter,
    Topic,
    LearningContent,
)

from quizzes.models import (
    Quiz,
    Question,
)


class Command(BaseCommand):
    help = (
        "Seed learning content and quizzes for "
        "KSEAB SSLC Mathematics Chapter 1 - Real Numbers"
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Real Numbers learning module..."
            )
        )

        # ---------------------------------------------------------
        # LOCATE CURRICULUM
        # ---------------------------------------------------------

        try:
            board = Board.objects.get(
                code="KSEAB"
            )

            academic_year = AcademicYear.objects.get(
                board=board,
                name="2026-27"
            )

            grade = Grade.objects.get(
                academic_year=academic_year,
                name="SSLC Class 10"
            )

            mathematics = Subject.objects.get(
                grade=grade,
                name="Mathematics"
            )

            chapter = Chapter.objects.get(
                subject=mathematics,
                chapter_number=1
            )

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
            Chapter.DoesNotExist,
        ):
            self.stdout.write(
                self.style.ERROR(
                    "KSEAB curriculum was not found. "
                    "Run 'python manage.py seed_kseab' first."
                )
            )

            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found chapter: {chapter}"
            )
        )

        # =========================================================
        # TOPIC 1
        # INTRODUCTION TO REAL NUMBERS
        # =========================================================

        topic_1 = Topic.objects.get(
            chapter=chapter,
            name="Introduction to Real Numbers"
        )

        LearningContent.objects.update_or_create(
            topic=topic_1,
            defaults={
                "explanation": (
                    "Real numbers include all rational numbers "
                    "and irrational numbers. They can be "
                    "represented on the number line. Natural "
                    "numbers, whole numbers, integers and "
                    "fractions that can be written in the form "
                    "p/q, where q is not zero, are rational "
                    "numbers. Numbers that cannot be expressed "
                    "in the form p/q are irrational numbers. "
                    "Together, rational and irrational numbers "
                    "form the set of real numbers."
                ),

                "key_concepts": (
                    "1. Natural numbers: 1, 2, 3, ...\n"
                    "2. Whole numbers: 0, 1, 2, 3, ...\n"
                    "3. Integers include positive numbers, "
                    "negative numbers and zero.\n"
                    "4. Rational numbers can be written as p/q "
                    "where p and q are integers and q is not 0.\n"
                    "5. Irrational numbers cannot be written "
                    "as p/q.\n"
                    "6. Rational numbers and irrational numbers "
                    "together make real numbers."
                ),

                "easy_method": (
                    "To classify a number:\n"
                    "Step 1: Check whether it is a counting "
                    "number.\n"
                    "Step 2: Check whether it is an integer.\n"
                    "Step 3: Check whether it can be written "
                    "as p/q.\n"
                    "Step 4: If it cannot be expressed as p/q, "
                    "it is irrational."
                ),

                "worked_example": (
                    "Example: Classify the number 3/5.\n\n"
                    "3/5 is already in the form p/q where "
                    "p = 3 and q = 5.\n"
                    "Since q is not zero, 3/5 is a rational "
                    "number.\n\n"
                    "Example: Classify √2.\n\n"
                    "√2 cannot be written exactly in the form "
                    "p/q for integers p and q. Therefore √2 "
                    "is an irrational number."
                ),

                "common_mistakes": (
                    "1. Thinking that every decimal number "
                    "is irrational.\n"
                    "2. Forgetting that terminating decimals "
                    "are rational.\n"
                    "3. Forgetting that repeating decimals "
                    "are also rational.\n"
                    "4. Thinking that zero is not a rational "
                    "number. Zero can be written as 0/1."
                ),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Learning content created: "
                "Introduction to Real Numbers"
            )
        )

        quiz_1, _ = Quiz.objects.update_or_create(
            topic=topic_1,
            title="Introduction to Real Numbers Quiz",
            defaults={
                "description": (
                    "Basic assessment on rational, "
                    "irrational and real numbers."
                )
            },
        )

        self._replace_questions(
            quiz_1,
            [
                {
                    "question_text": (
                        "Which of the following is a "
                        "rational number?"
                    ),
                    "option_a": "√2",
                    "option_b": "√3",
                    "option_c": "3/5",
                    "option_d": "π",
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "Which number is irrational?"
                    ),
                    "option_a": "0.5",
                    "option_b": "3/4",
                    "option_c": "√2",
                    "option_d": "7",
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "Which statement about rational "
                        "numbers is correct?"
                    ),
                    "option_a": (
                        "They cannot be written as fractions"
                    ),
                    "option_b": (
                        "They can be written as p/q where "
                        "q is not zero"
                    ),
                    "option_c": (
                        "They are always negative"
                    ),
                    "option_d": (
                        "They never contain decimals"
                    ),
                    "correct_answer": "B",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "Which of the following belongs "
                        "to the set of real numbers?"
                    ),
                    "option_a": "Only integers",
                    "option_b": "Only rational numbers",
                    "option_c": "Only irrational numbers",
                    "option_d": (
                        "Both rational and irrational numbers"
                    ),
                    "correct_answer": "D",
                    "difficulty": 2,
                },
                {
                    "question_text": (
                        "Which of the following is rational?"
                    ),
                    "option_a": "π",
                    "option_b": "√5",
                    "option_c": "0.25",
                    "option_d": "√7",
                    "correct_answer": "C",
                    "difficulty": 2,
                },
            ],
        )

        # =========================================================
        # TOPIC 2
        # FUNDAMENTAL THEOREM OF ARITHMETIC
        # =========================================================

        topic_2 = Topic.objects.get(
            chapter=chapter,
            name="Fundamental Theorem of Arithmetic"
        )

        LearningContent.objects.update_or_create(
            topic=topic_2,
            defaults={
                "explanation": (
                    "The Fundamental Theorem of Arithmetic "
                    "states that every composite number can "
                    "be expressed as a product of prime "
                    "numbers in a unique way, except for the "
                    "order of the prime factors. Prime "
                    "factorisation is useful for finding "
                    "HCF and LCM and for studying properties "
                    "of numbers."
                ),

                "key_concepts": (
                    "1. A prime number has exactly two "
                    "positive factors: 1 and itself.\n"
                    "2. A composite number has more than "
                    "two positive factors.\n"
                    "3. Every composite number can be "
                    "expressed as a product of primes.\n"
                    "4. Prime factorisation is unique apart "
                    "from the order of the factors.\n"
                    "5. HCF uses the lowest powers of common "
                    "prime factors.\n"
                    "6. LCM uses the highest powers of all "
                    "prime factors."
                ),

                "easy_method": (
                    "Prime factorisation method:\n"
                    "Step 1: Divide the number by the "
                    "smallest possible prime number.\n"
                    "Step 2: Continue dividing the quotient "
                    "by prime numbers.\n"
                    "Step 3: Stop when the quotient becomes "
                    "1.\n"
                    "Step 4: Write the number as the product "
                    "of all prime divisors."
                ),

                "worked_example": (
                    "Example: Prime factorise 60.\n\n"
                    "60 = 2 × 30\n"
                    "30 = 2 × 15\n"
                    "15 = 3 × 5\n\n"
                    "Therefore:\n"
                    "60 = 2 × 2 × 3 × 5\n"
                    "60 = 2² × 3 × 5."
                ),

                "common_mistakes": (
                    "1. Using composite numbers as final "
                    "factors.\n"
                    "2. Forgetting repeated prime factors.\n"
                    "3. Using highest powers while calculating "
                    "HCF.\n"
                    "4. Using lowest powers while calculating "
                    "LCM."
                ),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Learning content created: "
                "Fundamental Theorem of Arithmetic"
            )
        )

        quiz_2, _ = Quiz.objects.update_or_create(
            topic=topic_2,
            title=(
                "Fundamental Theorem of Arithmetic Quiz"
            ),
            defaults={
                "description": (
                    "Assessment on prime factorisation, "
                    "HCF and LCM."
                )
            },
        )

        self._replace_questions(
            quiz_2,
            [
                {
                    "question_text": (
                        "Which of the following is a "
                        "prime number?"
                    ),
                    "option_a": "9",
                    "option_b": "15",
                    "option_c": "17",
                    "option_d": "21",
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "What is the prime factorisation "
                        "of 12?"
                    ),
                    "option_a": "2 × 6",
                    "option_b": "2² × 3",
                    "option_c": "3 × 4",
                    "option_d": "1 × 12",
                    "correct_answer": "B",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "The Fundamental Theorem of "
                        "Arithmetic mainly concerns:"
                    ),
                    "option_a": "Geometry",
                    "option_b": "Prime factorisation",
                    "option_c": "Trigonometry",
                    "option_d": "Probability",
                    "correct_answer": "B",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "If 24 = 2³ × 3 and "
                        "36 = 2² × 3², what is their HCF?"
                    ),
                    "option_a": "6",
                    "option_b": "12",
                    "option_c": "24",
                    "option_d": "72",
                    "correct_answer": "B",
                    "difficulty": 2,
                },
                {
                    "question_text": (
                        "If 12 = 2² × 3 and "
                        "18 = 2 × 3², what is their LCM?"
                    ),
                    "option_a": "6",
                    "option_b": "18",
                    "option_c": "24",
                    "option_d": "36",
                    "correct_answer": "D",
                    "difficulty": 2,
                },
                {
                    "question_text": (
                        "The prime factorisation of a "
                        "composite number is:"
                    ),
                    "option_a": "Always different",
                    "option_b": (
                        "Unique apart from the order "
                        "of factors"
                    ),
                    "option_c": "Impossible to determine",
                    "option_d": "Always two factors",
                    "correct_answer": "B",
                    "difficulty": 3,
                },
            ],
        )

        # =========================================================
        # TOPIC 3
        # IRRATIONAL NUMBERS
        # =========================================================

        topic_3 = Topic.objects.get(
            chapter=chapter,
            name="Revisiting Irrational Numbers"
        )

        LearningContent.objects.update_or_create(
            topic=topic_3,
            defaults={
                "explanation": (
                    "An irrational number is a real number "
                    "that cannot be expressed in the form "
                    "p/q, where p and q are integers and "
                    "q is not zero. Its decimal expansion "
                    "is non-terminating and non-repeating. "
                    "Examples include √2, √3, √5 and π."
                ),

                "key_concepts": (
                    "1. Irrational numbers cannot be "
                    "expressed as p/q.\n"
                    "2. Their decimal expansions are "
                    "non-terminating and non-repeating.\n"
                    "3. √2, √3 and √5 are common examples.\n"
                    "4. Rational and irrational numbers "
                    "are both real numbers."
                ),

                "easy_method": (
                    "To identify common irrational numbers:\n"
                    "Step 1: Check whether the number is the "
                    "square root of a perfect square.\n"
                    "Step 2: If it is a perfect square, its "
                    "square root is rational.\n"
                    "Step 3: If it is not a perfect square, "
                    "its square root is generally irrational."
                ),

                "worked_example": (
                    "Example: Determine whether √9 is "
                    "rational or irrational.\n\n"
                    "√9 = 3.\n"
                    "3 can be written as 3/1.\n"
                    "Therefore √9 is rational.\n\n"
                    "Example: √7 cannot be simplified to "
                    "an integer because 7 is not a perfect "
                    "square. Therefore √7 is irrational."
                ),

                "common_mistakes": (
                    "1. Assuming every square root is "
                    "irrational.\n"
                    "2. Forgetting that √4 = 2 and √9 = 3 "
                    "are rational.\n"
                    "3. Confusing non-terminating repeating "
                    "decimals with irrational numbers. "
                    "Repeating decimals are rational."
                ),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Learning content created: "
                "Revisiting Irrational Numbers"
            )
        )

        quiz_3, _ = Quiz.objects.update_or_create(
            topic=topic_3,
            title="Irrational Numbers Quiz",
            defaults={
                "description": (
                    "Assessment on irrational numbers "
                    "and decimal expansions."
                )
            },
        )

        self._replace_questions(
            quiz_3,
            [
                {
                    "question_text": (
                        "Which of the following is "
                        "irrational?"
                    ),
                    "option_a": "√16",
                    "option_b": "√25",
                    "option_c": "√7",
                    "option_d": "0.5",
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "The decimal expansion of an "
                        "irrational number is:"
                    ),
                    "option_a": (
                        "Always terminating"
                    ),
                    "option_b": (
                        "Always repeating"
                    ),
                    "option_c": (
                        "Non-terminating and non-repeating"
                    ),
                    "option_d": (
                        "Always a whole number"
                    ),
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "Which of the following is rational?"
                    ),
                    "option_a": "√2",
                    "option_b": "√3",
                    "option_c": "√9",
                    "option_d": "√11",
                    "correct_answer": "C",
                    "difficulty": 1,
                },
                {
                    "question_text": (
                        "Why is √5 irrational?"
                    ),
                    "option_a": (
                        "Because 5 is an even number"
                    ),
                    "option_b": (
                        "Because 5 is not a perfect square"
                    ),
                    "option_c": (
                        "Because 5 is negative"
                    ),
                    "option_d": (
                        "Because 5 is a fraction"
                    ),
                    "correct_answer": "B",
                    "difficulty": 2,
                },
                {
                    "question_text": (
                        "Which pair contains only "
                        "irrational numbers?"
                    ),
                    "option_a": "√2 and √3",
                    "option_b": "√4 and √9",
                    "option_c": "1/2 and √5",
                    "option_d": "0.25 and 3",
                    "correct_answer": "A",
                    "difficulty": 2,
                },
            ],
        )

        # =========================================================
        # FINAL SUMMARY
        # =========================================================

        total_topics = chapter.topics.count()

        total_lessons = LearningContent.objects.filter(
            topic__chapter=chapter
        ).count()

        total_quizzes = Quiz.objects.filter(
            topic__chapter=chapter
        ).count()

        total_questions = Question.objects.filter(
            quiz__topic__chapter=chapter
        ).count()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Real Numbers module seeded successfully."
            )
        )

        self.stdout.write("")
        self.stdout.write(
            f"Chapter: {chapter.name}"
        )

        self.stdout.write(
            f"Topics: {total_topics}"
        )

        self.stdout.write(
            f"Learning contents: {total_lessons}"
        )

        self.stdout.write(
            f"Quizzes: {total_quizzes}"
        )

        self.stdout.write(
            f"Questions: {total_questions}"
        )

    # =============================================================
    # QUESTION HELPER
    # =============================================================

    def _replace_questions(
        self,
        quiz,
        questions,
    ):

        # This keeps the seed command repeatable.
        # Existing questions for this seeded quiz are replaced
        # rather than duplicated every time the command runs.

        quiz.questions.all().delete()

        for data in questions:

            Question.objects.create(
                quiz=quiz,
                question_text=data["question_text"],
                option_a=data["option_a"],
                option_b=data["option_b"],
                option_c=data["option_c"],
                option_d=data["option_d"],
                correct_answer=data["correct_answer"],
                difficulty=data["difficulty"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Quiz ready: {quiz.title} "
                f"({len(questions)} questions)"
            )
        )