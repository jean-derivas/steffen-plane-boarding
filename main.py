import itertools
from dataclasses import dataclass
from typing import Dict, Tuple, List, Iterator

import matplotlib.pyplot as plt
import pandas as pd


@dataclass(repr=True, eq=True)
class Seat(object):
    row: str
    side: str
    distance: int

    def __init__(self, row, side, distance):
        self.row = row
        self.side = side
        self.distance = distance

    def seat_to_classic_position(self, length: int) -> str:
        list_row_names = [
            "".join(row)
            for row in itertools.chain(
                *[itertools.product(map(chr, range(65, 91)), repeat=i) for i in range(1, 3)]
            )
        ]
        """
        Transform seat modelisation to classic position for a passenger
        Args:
            length: length of the plane (total number of row)

        Returns:
            seat as str like "3C"
        """
        classic_row_from_behind = list_row_names.index(self.row)
        classic_row = length - classic_row_from_behind
        letters_available = ("A", "B", "C", "D", "E", "F")
        if self.side == "L":
            idx = 2 - self.distance + 1
        else:
            idx = 2 + self.distance
        letter = letters_available[idx]

        return f"{classic_row}{letter}"

    def __hash__(self):
        return hash((self.row, self.side, self.distance))


def invert_dict(zdict):
    return dict((reversed(item) for item in zdict.items()))


def row_names(length):
    list_row_names = [
        "".join(row)
        for row in itertools.chain(
            *[itertools.product(map(chr, range(65, 91)), repeat=i) for i in range(1, 3)]
        )
    ]
    return {i: list_row_names[i] for i in range(len(list_row_names[:length]))}


class Problem(object):
    def __init__(self, length: int):
        self.length = length
        self.dict_of_rows = row_names(self.length)
        self.row_to_position = invert_dict(self.dict_of_rows)
        self.plane, self.passengers_to_seat, self.seat_to_passengers = self._generate_flight()
        self.optimal_allocation = None
        self._charging = []

    def get_optimal_seats_boarding_order(self) -> List[Seat]:
        """This methods return and store a list containing the seat, ordered with optimal method of steffen"""
        seats = []
        side = "L"
        for distance in 3, 2, 1:
            for pair in range(2):
                for i, row in self.dict_of_rows.items():
                    self._add_seat(distance, i, pair, row, seats, side)
                side = "L" if side == "R" else "R"
                for i, row in self.dict_of_rows.items():
                    self._add_seat(distance, i, pair, row, seats, side)
                side = "L" if side == "R" else "R"
        self.optimal_allocation = seats
        return self.optimal_allocation

    def play_boarding(self, name=None):
        ended = False
        all_checked = False
        passenger_iter = self.get_next_passenger_to_onboard()
        total_time_for_boarding = 0
        while not ended and not self.somebody_arrived(name):
            while not all_checked and not self.somebody_arrived(name):
                if self.plane[3][0] == 1:
                    try:
                        self.plane[3][0] = next(passenger_iter)
                    except StopIteration:
                        all_checked = True
                self.move_passengers()
                total_time_for_boarding += 1

            self.move_passengers()
            if self._all_passengers_seated():
                ended = True
            total_time_for_boarding += 1

        return total_time_for_boarding

    def get_next_passenger_to_onboard(self) -> Iterator[str]:
        """
        Iterator returned to give next passenger to onboard
        Returns:
            an iterator over ordered passenger list
        """
        for seat in self.optimal_allocation:
            yield self.seat_to_passengers.get(seat)

    def somebody_arrived(self, name):
        if name is None:
            return False
        seat = self.passengers_to_seat[name]
        x, y = self._seat_to_index(seat)
        if self.plane[y][x] == name:
            return True
        else:
            return False

    def move_passengers(self):
        for k in range(self.length + 10):
            if isinstance(self.plane[3][self.length + 9 - k], str):  # if it is somebody
                # self.length + 9 - k + 1 > self.length + 9 or
                x, y = self._seat_to_index(
                    self.passengers_to_seat[self.plane[3][self.length + 9 - k]])  # get target pos
                if self.plane[3][self.length + 9 - k] in self._charging:  # if charging, then go to right place
                    self.plane[y][x] = self.plane[3][self.length + 9 - k]
                    self.plane[3][self.length + 9 - k] = 1
                    self._charging.remove(self.plane[y][x])
                elif x == self.length + 9 - k:  # if at the good x value, charge lugagge
                    self._charging.append(self.plane[3][self.length + 9 - k])
                if (
                        self.length + 9 - k + 1 >= self.length + 10 or
                        isinstance(self.plane[3][self.length + 9 - k + 1], str)
                ):  # if it is blocked by somebody
                    continue
                self.plane[3][self.length + 9 - k + 1] = self.plane[3][self.length + 9 - k]
                self.plane[3][self.length + 9 - k] = 1

    def time_to_board(self, specific_passenger=None):
        return self.play_boarding(specific_passenger)

    def get_passenger_position(self, name: str) -> int:
        """
        Give the passenger position call given its name
        Args:
            name: the name of the passenger

        Returns:
            the call position
        """
        return self.optimal_allocation.index(self.passengers_to_seat.get(name))

    def _seat_to_index(self, seat):
        x = self.length + 9 - self.row_to_position[seat.row]
        if seat.side == "L":
            y = 3 + seat.distance
        else:
            y = 3 - seat.distance
        return x, y

    def _generate_passengers(self) -> Tuple[Dict[str, Seat], Dict[Seat, str]]:
        passengers_to_seat = {}
        ct = 0
        for i, row in self.dict_of_rows.items():
            for side in "L", "R":
                for distance in 1, 2, 3:
                    passengers_to_seat[f"name_{ct}"] = Seat(row, side, distance)
                    ct += 1
        seat_to_passengers = invert_dict(passengers_to_seat)
        return passengers_to_seat, seat_to_passengers

    def _generate_plane(self) -> List[List[int]]:
        """zeros are not accessible land and ones are accessible (corridor or seats)"""
        plane = [[1 for _ in range(self.length + 10)] for _ in range(7)]
        for k in range(10):  # length of the corridor outside the plane
            for j in range(7):
                if j == 3:  # only the central part on the outside corridor is accessible
                    continue
                plane[j][k] = 0
        return plane

    def _generate_flight(self) -> Tuple[List[List[int]], Dict[str, Seat], Dict[Seat, str]]:
        """
        Generate the flight, generate the plane map and the passengers and seats associated
        Returns:
            the map, the passengers to seat and seat to passengers
        """
        pax_to_seat, seat_to_pax = self._generate_passengers()
        return self._generate_plane(), pax_to_seat, seat_to_pax

    def _all_passengers_seated(self):
        """Check if all passengers are seated <=> there is no passenger in the corridor (assumption here)
        Todo: Check also seats compared to list of passengers to be more robust
        Returns:
            bool value if all passengers are seated
        """
        all_seated = True
        for k in range(self.length + 10):
            if self.plane[3][k] != 1:
                all_seated = False
                break
        return all_seated

    def _add_seat(self, distance, i, pair, row, seats, side):
        """add a seat to the list seats for optimal allocation onboard
        Args:
            distance:
            i:
            pair:
            row:
            seats:
            side:
        """
        if (i + pair) % 2 == 0:
            seats.append(Seat(row, side, distance))


def total_time_boarding_per_size():
    zdict = {}
    for i in range(1, 60):
        pb = Problem(i)
        pb.get_optimal_seats_boarding_order()
        total = pb.play_boarding()
        print(f"total time : {total}")
        zdict[i] = total
    return zdict


def plot_complexity_accross_size():
    output = total_time_boarding_per_size()

    df = pd.DataFrame(output.values(), output.keys())
    df.plot.line()
    plt.show()


if __name__ == '__main__':
    pb = Problem(30)
    pb.get_optimal_seats_boarding_order()
    time = pb.play_boarding()
