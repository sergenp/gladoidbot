from typing import List, Type, Dict, Callable, Union
import json
import pathlib

path = pathlib.Path(__file__).parent.absolute()


class Question:
    def __init__(self, body: Type[str], options: List[str], Id=-1):
        self.Id = Id
        self.body = body
        self.options = options
        self.answer = ""

    def answer_question(self, answer):
        if answer in self.options:
            self.answer = answer
        else:
            raise ValueError(f"{answer} is not in {self.options}")

    def to_json(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return f"Id: {self.Id}, Q: {self.body}, A: {self.answer}"


QuestionsType = Union[List[Question], Dict[int, Question]]


class TestNode:
    def __init__(self, question: Question):
        self.question = question
        self.next = None
        self.prev = None


class Test:
    def __init__(
        self,
        test_id,
        questions: QuestionsType,
        scoring_function: Callable[[QuestionsType], Dict[str, str]],
    ):
        self.test_id = test_id
        self.is_finished = False
        self.head = None
        self.scoring_function = scoring_function
        self.questions = questions

        if type(questions) == dict:
            for q in questions.values():
                self.add_questions(q)
        else:
            for q in questions:
                self.add_questions(q)

        self.current = self.head

    def add_questions(self, new_question: Question):
        NewNode = TestNode(new_question)
        NewNode.next = self.head
        if self.head is not None:
            self.head.prev = NewNode
        self.head = NewNode

    def get_next_question(self) -> Question:
        if self.current.next is not None:
            self.current = self.current.next
            return self.current.question

    def get_previous_question(self) -> Question:
        if self.current.prev is not None:
            self.current = self.current.prev
            return self.current.question

    def get_current_question(self) -> Question:
        if self.current is not None:
            return self.current.question

    def answer_question(self, answer):
        if self.current:
            self.current.question.answer_question(answer)
        else:
            raise ValueError("Current question is None")

    def answer_specific_question(self, answer, Id):
        self.current = self.head
        while self.current:
            if self.current.question.Id == Id:
                self.current.question.answer_question(answer)
                break
            self.current = self.current.next
        else:
            raise ValueError(f"Question with Id: {Id} couldn't been found")

    def end_test(self):
        ### let's check if every question is answered,
        unanswered_questions = []
        temp = self.head
        while temp:
            if not temp.question.answer:
                unanswered_questions.append(temp.question.Id)
            temp = temp.next

        if not unanswered_questions:
            return self.scoring_function(self.questions)
        else:
            return {
                "error": {
                    "detail": "There are unanswered questions",
                    "unanswered_questions": unanswered_questions,
                }
            }


class Big5Test(Test):
    def __init__(self, test_id):
        with open(path / "questions.txt", "r") as f:
            question_data = [x.replace("\n", "").split(".") for x in f.readlines()]

        # reverse the list because Test class uses a doubly linked list,
        # Test.add_questions method insert the data where the head is,
        # works like a stack, last in first out style
        question_data = reversed(sorted(question_data, key=lambda x: int(x[0])))
        self._question_dct = {}
        for question in question_data:
            q = Question(Id=int(question[0]), body=question[1], options=[1, 2, 3, 4, 5])
            self._question_dct[int(question[0])] = q

        super().__init__(
            test_id=test_id,
            questions=self._question_dct,
            scoring_function=Big5Test.big_five_scoring,
        )

    @staticmethod
    def big_five_scoring(question_dct):
        E_operators = "+-+-+-+-+-"
        A_operators = "-+-+-+-+++"
        C_operators = "+-+-+-+-++"
        N_operators = "-+-+------"
        O_operators = "+-+-+-++++"
        O, C, E, A, N = 8, 14, 20, 14, 38
        op_index = 0
        for i in range(1, len(question_dct.values()) + 1):
            if i % 5 == 1:
                op = E_operators[op_index]
                E = eval(f"E{op}{question_dct[i].answer}")
            elif i % 5 == 2:
                op = A_operators[op_index]
                A = eval(f"A{op}{question_dct[i].answer}")
            elif i % 5 == 3:
                op = C_operators[op_index]
                C = eval(f"C{op}{question_dct[i].answer}")
            elif i % 5 == 4:
                op = N_operators[op_index]
                N = eval(f"N{op}{question_dct[i].answer}")
            elif i % 5 == 0:
                op = O_operators[op_index]
                O = eval(f"O{op}{question_dct[i].answer}")
                op_index += 1
        O, C, E, A, N = (
            (O / 40) * 100,
            (C / 40) * 100,
            (E / 40) * 100,
            (A / 40) * 100,
            (N / 40) * 100,
        )

        return {
            "Openness": f"{O:.2f}%",
            "Conscientiousness": f"{C:.2f}%",
            "Extroversion": f"{E:.2f}%",
            "Agreeableness": f"{A:.2f}%",
            "Neuroticism": f"{N:.2f}%",
        }
