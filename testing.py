import appointments

def runConflictTests():

    tests = [

        (
            "Staff Conflict",
            True,
            appointments.checkConflict(
                "2026-09-18",
                "10:15",
                30,
                2,
                6
            )
        ),

        (
            "Patient Conflict",
            True,
            appointments.checkConflict(
                "2026-09-18",
                "10:15",
                30,
                1,
                1
            )
        ),

        (
            "Back To Back",
            False,
            appointments.checkConflict(
                "2026-09-18",
                "11:00",
                30,
                2,
                6
            )
        ),

        (
            "No Conflict",
            False,
            appointments.checkConflict(
                "2026-09-18",
                "10:00",
                30,
                1,
                6
            )
        )
    ]

    print("\n=== Conflict Detection Tests ===\n")

    for name, expected, actual in tests:

        if expected == actual:
            print(f"{name}: PASS")

        else:
            print(f"{name}: FAIL")
            print(f"Expected: {expected}")
            print(f"Actual:   {actual}")

if __name__ == "__main__":
    runConflictTests()