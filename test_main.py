from main import row_names, Problem, Seat


def test_row_names():
    assert row_names(0) == {}
    assert row_names(1) == {0: 'A'}
    assert row_names(2) == {0: 'A', 1: 'B'}
    alphabet = {i:k for i, k in enumerate(list(map(chr, range(65, 91))))}
    assert row_names(26) == alphabet
    assert row_names(30) == {**alphabet, **{26: "AA", 27: "AB", 28: "AC", 29: "AD"}}


def test_generate_passengers():
    pb = Problem(30)
    assert len(pb.passengers_to_seat) == len(pb.seat_to_passengers) == 30 * 6
    for k, v in pb.passengers_to_seat.items():
        assert pb.seat_to_passengers.get(v) == k


def test_get_optimal_seats_boarding_order():
    pb = Problem(5)
    pb.get_optimal_seats_boarding_order()
    assert pb.optimal_allocation == [
        Seat(row='A', side='L', distance=3),
        Seat(row='C', side='L', distance=3),
        Seat(row='E', side='L', distance=3),
        Seat(row='A', side='R', distance=3),
        Seat(row='C', side='R', distance=3),
        Seat(row='E', side='R', distance=3),
        Seat(row='B', side='L', distance=3),
        Seat(row='D', side='L', distance=3),
        Seat(row='B', side='R', distance=3),
        Seat(row='D', side='R', distance=3),
        Seat(row='A', side='L', distance=2),
        Seat(row='C', side='L', distance=2),
        Seat(row='E', side='L', distance=2),
        Seat(row='A', side='R', distance=2),
        Seat(row='C', side='R', distance=2),
        Seat(row='E', side='R', distance=2),
        Seat(row='B', side='L', distance=2),
        Seat(row='D', side='L', distance=2),
        Seat(row='B', side='R', distance=2),
        Seat(row='D', side='R', distance=2),
        Seat(row='A', side='L', distance=1),
        Seat(row='C', side='L', distance=1),
        Seat(row='E', side='L', distance=1),
        Seat(row='A', side='R', distance=1),
        Seat(row='C', side='R', distance=1),
        Seat(row='E', side='R', distance=1),
        Seat(row='B', side='L', distance=1),
        Seat(row='D', side='L', distance=1),
        Seat(row='B', side='R', distance=1),
        Seat(row='D', side='R', distance=1)
    ]


