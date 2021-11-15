from data import get_questions_and_answers


def main():
    for question, answer in get_questions_and_answers().items():
        print(question, answer)


if __name__ == '__main__':
    main()
