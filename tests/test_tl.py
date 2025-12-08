from child_ai.logic_engine import Predicate, Constant, TemporalRule, LogicEngine

def test_temporal_reasoning_before():
    engine = LogicEngine()
    engine.add_fact(Predicate("HappensAt", (Predicate("Login", (Constant("UserA"),)), Constant("100"))))
    engine.add_fact(Predicate("HappensAt", (Predicate("Logout", (Constant("UserA"),)), Constant("200"))))

    query = TemporalRule("Before", (
        Predicate("Login", (Constant("UserA"),)),
        Predicate("Logout", (Constant("UserA"),))
    ))

    assert engine.query(query) == True

def test_temporal_reasoning_after():
    engine = LogicEngine()
    engine.add_fact(Predicate("HappensAt", (Predicate("Login", (Constant("UserA"),)), Constant("100"))))
    engine.add_fact(Predicate("HappensAt", (Predicate("Logout", (Constant("UserA"),)), Constant("200"))))

    query = TemporalRule("After", (
        Predicate("Logout", (Constant("UserA"),)),
        Predicate("Login", (Constant("UserA"),))
    ))

    assert engine.query(query) == True
