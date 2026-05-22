
from __future__ import annotations

from dataclasses import dataclass
from random import randint, random, seed
from time import sleep


MIN_GREEN_SECONDS = 8
MAX_GREEN_SECONDS = 45
YELLOW_SECONDS = 3
LANE_CAPACITY = 50


@dataclass
class Lane:
    name: str
    vehicle_count: int
    arrival_rate: int
    waiting_time: int = 0
    emergency_vehicle: bool = False

    @property
    def density(self) -> float:
        return min(self.vehicle_count / LANE_CAPACITY, 1.0)

    @property
    def density_label(self) -> str:
        if self.density >= 0.75:
            return "High"
        if self.density >= 0.40:
            return "Medium"
        return "Low"


class AITrafficController:
    """Choose signals from traffic density instead of a fixed rotation."""

    def __init__(self, lanes: list[Lane]) -> None:
        self.lanes = lanes
        self.current_green: str | None = None

    def urgency_score(self, lane: Lane) -> float:
        density_score = lane.density * 60
        queue_score = lane.vehicle_count * 1.5
        wait_score = min(lane.waiting_time, 120) * 0.35
        arrival_score = lane.arrival_rate * 2
        emergency_score = 100 if lane.emergency_vehicle else 0
        return density_score + queue_score + wait_score + arrival_score + emergency_score

    def choose_green_lane(self) -> Lane:
        return max(self.lanes, key=self.urgency_score)

    def green_duration(self, lane: Lane) -> int:
        duration = MIN_GREEN_SECONDS + round(lane.density * 30) + lane.arrival_rate
        if lane.emergency_vehicle:
            duration += 8
        return max(MIN_GREEN_SECONDS, min(duration, MAX_GREEN_SECONDS))

    def update_traffic(self, green_lane: Lane, green_seconds: int) -> None:
        vehicles_cleared = min(green_lane.vehicle_count, green_seconds * 2)

        for lane in self.lanes:
            new_vehicles = randint(max(0, lane.arrival_rate - 2), lane.arrival_rate + 4)
            lane.vehicle_count = min(LANE_CAPACITY, lane.vehicle_count + new_vehicles)

            if lane is green_lane:
                lane.vehicle_count = max(0, lane.vehicle_count - vehicles_cleared)
                lane.waiting_time = 0
                lane.emergency_vehicle = False
            else:
                lane.waiting_time += green_seconds + YELLOW_SECONDS
                lane.emergency_vehicle = lane.emergency_vehicle or random() < 0.04

    def print_status(self, cycle: int, green_lane: Lane, green_seconds: int) -> None:
        print(f"\nCycle {cycle}")
        print(f"Green signal: {green_lane.name} for {green_seconds} seconds")
        print(f"Yellow signal: all roads for {YELLOW_SECONDS} seconds")
        print("-" * 74)
        print(f"{'Road':<14}{'Vehicles':<12}{'Density':<10}{'Wait':<10}{'Emergency':<12}{'Score'}")
        print("-" * 74)

        for lane in self.lanes:
            emergency = "Yes" if lane.emergency_vehicle else "No"
            print(
                f"{lane.name:<14}"
                f"{lane.vehicle_count:<12}"
                f"{lane.density_label:<10}"
                f"{lane.waiting_time:<10}"
                f"{emergency:<12}"
                f"{self.urgency_score(lane):.1f}"
            )

    def run(self, cycles: int = 10, pause_seconds: float = 0.6) -> None:
        for cycle in range(1, cycles + 1):
            green_lane = self.choose_green_lane()
            green_seconds = self.green_duration(green_lane)
            self.current_green = green_lane.name

            self.print_status(cycle, green_lane, green_seconds)
            self.update_traffic(green_lane, green_seconds)
            sleep(pause_seconds)


def create_sample_junction() -> list[Lane]:
    return [
        Lane("North Road", vehicle_count=34, arrival_rate=7),
        Lane("South Road", vehicle_count=18, arrival_rate=5),
        Lane("East Road", vehicle_count=42, arrival_rate=8),
        Lane("West Road", vehicle_count=11, arrival_rate=3),
    ]


def read_positive_int(prompt: str, default: int) -> int:
    raw_value = input(prompt).strip()
    if not raw_value:
        return default
    while not raw_value.isdigit() or int(raw_value) <= 0:
        raw_value = input("Please enter a positive number: ").strip()
    return int(raw_value)


def main() -> None:
    print("AI-Based Smart Traffic Light Controller")
    print("Signals are selected from density, queue size, wait time, and emergency priority.")

    cycles = read_positive_int("\nHow many signal cycles should be simulated? [10]: ", 10)
    controller = AITrafficController(create_sample_junction())
    controller.run(cycles=cycles)

    print("\nSimulation complete. The highest-urgency road received priority each cycle.")


if __name__ == "__main__":
    seed()
    main()
