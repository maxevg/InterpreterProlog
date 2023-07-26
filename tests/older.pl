% Это факты
older(misha, sasha, fact). % Миша старше Саши
older(misha, julia, fact). % Миша старше Даши
older(masha, misha, fact). % Маша старше Миши

% Это правило
older(X,Y, rule) :- older(X, Z, fact), older(Z,Y, _).