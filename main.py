#-*- coding: utf-8 -*-

import re
import codecs
from prolog.interpreter import Database, Variable, Rule
from prolog.parser import Parser
from prolog.scanner import Scanner
from prolog.types import FALSE, CUT, Dot, Bar, Arithmetic

DATABASE = r"^\[[A-Za-z0-9_]+\]\."


def display_answer(goal, solution, stream_reader = None):
    if stream_reader is not None:
        print(stream_reader(), end='')
    has_variables = False
    if isinstance(goal, Rule):
        goal = goal.head
    for arg in goal.args:
        if isinstance(arg, Variable):
            goal_match = goal.match(solution)
            if goal_match:
                bind = goal_match.get(arg)
                print(f'{arg} = {bind}')
                has_variables = True
        elif isinstance(arg, Dot):
            goal_match = goal.match(solution)
            if isinstance(arg, Dot) and goal_match:
                for k, v in goal_match.items():
                    if isinstance(k, Variable) and k.name == '_':
                        continue
                    print(f'{k} = {v}', end=' ')
                has_variables = True
        elif isinstance(arg, Bar):
            goal_match = goal.match(solution)
            if goal_match:
                for k, v in goal_match.items():
                    if isinstance(k, Variable) and k.name == '_':
                        continue
                    print(f'{k} = {v}', end=' ')
                has_variables = True
    if has_variables:
        print('')


if __name__ == '__main__':
    database = None
    haveData = False
    while True:
        query = input("?- ")

        if re.match(DATABASE, query):
            file_name = query[1: len(query) - 2]

            try:
                with codecs.open('tests\\' + file_name + '.pl', 'r', encoding='utf8') as database_file:
                    database_content = database_file.read()
            except:
                print("ERROR: source '" + file_name + ".pl' does not exist")
            rules = Parser(
                Scanner(database_content).tokenize()
            ).parse()

            database = Database(rules)
            haveData = True
            print("true.\n")

        else:
            goal = Parser(
                Scanner(query).tokenize()
            ).parse_query()
            if haveData:
                database.reset_stream()

                is_first_iter = False
                has_solution = False
                for solution in database.execute(goal):
                    if isinstance(solution, CUT):
                        break
                    if not isinstance(solution, FALSE):
                        has_solution = True
                    if is_first_iter is False:
                        is_first_iter = True
                    else:
                        ch = input()
                        if ch == ';':
                            has_solution = False
                        else:
                            has_solution = False
                            break

                    display_answer(goal, solution, database.stream_read)
                if has_solution:
                    print('true')
                else:
                    if not is_first_iter:
                        print(database.stream_read(), end='')
                    print('false')
            elif isinstance(goal, Arithmetic):
                display_answer(goal, goal.evaluate())
            else:
                print('false')

