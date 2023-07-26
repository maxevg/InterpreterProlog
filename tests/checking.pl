% workers
worker(alex).
worker(sam).
worker(matt).


on_work(alex).
off_work(matt).


% rules
came_to_work(X) :-
    on_work(X),
    write(X), write(' is already on work!'), nl,
    !, fail.

came_to_work(X) :-
    off_work(X),
    retract(off_work(X)),
    assertz(on_work(X)),
    write('Came to work '), write(X), nl, !.

came_to_work(X) :-
    write('Cannot execute '), write(X), nl,
    fail.

came_off_work(X) :-
    off_work(X),
    write(X), write(' is already off work!'), nl,
    !, fail.

came_off_work(X) :-
    on_work(X),
    retract(on_work(X)),
    assertz(off_work(X)),
    write('Came off work'), write(X), nl, !.

came_off_work(X) :-
    write('Cannot execute '), write(X), nl,
    fail.

current_hour(8).