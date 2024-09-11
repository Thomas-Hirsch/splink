import pandas as pd

import splink.comparison_library as cl
import splink.internals.comparison_level_library as cll
from splink import ColumnExpression
from tests.literal_utils import run_comparison_vector_value_tests, run_is_in_level_tests

from .decorator import mark_with_dialects_excluding


@mark_with_dialects_excluding()
def test_columns_reversed_level(test_helpers, dialect):
    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    test_cases = [
        {
            "description": "Basic ColumnsReversedLevel, not symmetrical",
            "level": cll.ColumnsReversedLevel("forename", "surname"),
            "inputs": [
                {
                    "forename_l": "John",
                    "forename_r": "Smith",
                    "surname_l": "Smith",
                    "surname_r": "John",
                    "expected": True,
                },
                {
                    "forename_l": "Smith",
                    "forename_r": "John",
                    "surname_l": "John",
                    "surname_r": "Smith",
                    "expected": True,
                },
                {
                    "forename_l": "John",
                    "forename_r": "John",
                    "surname_l": "Smith",
                    "surname_r": "Smith",
                    "expected": False,
                },
            ],
        },
        {
            "description": "ColumnsReversedLevel with symmetrical=True",
            "level": cll.ColumnsReversedLevel("forename", "surname", symmetrical=True),
            "inputs": [
                {
                    "forename_l": "John",
                    "forename_r": "Smith",
                    "surname_l": "Smith",
                    "surname_r": "John",
                    "expected": True,
                },
                {
                    "forename_l": "Smith",
                    "forename_r": "John",
                    "surname_l": "John",
                    "surname_r": "Smith",
                    "expected": True,
                },
                {
                    "forename_l": "John",
                    "forename_r": "John",
                    "surname_l": "Smith",
                    "surname_r": "Smith",
                    "expected": False,
                },
            ],
        },
        {
            "description": "ColumnsReversedLevel with ColumnExpression",
            "level": cll.ColumnsReversedLevel(
                ColumnExpression("forename").lower(),
                ColumnExpression("surname").lower(),
            ),
            "inputs": [
                {
                    "forename_l": "John",
                    "forename_r": "SMITH",
                    "surname_l": "Smith",
                    "surname_r": "JOHN",
                    "expected": True,
                },
                {
                    "forename_l": "JOHN",
                    "forename_r": "smith",
                    "surname_l": "SMITH",
                    "surname_r": "john",
                    "expected": True,
                },
                {
                    "forename_l": "John",
                    "forename_r": "John",
                    "surname_l": "Smith",
                    "surname_r": "Smith",
                    "expected": False,
                },
            ],
        },
    ]

    run_is_in_level_tests(test_cases, db_api)


@mark_with_dialects_excluding()
def test_perc_difference(test_helpers, dialect):
    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    perc_comparison = cl.CustomComparison(
        comparison_description="amount",
        comparison_levels=[
            cll.NullLevel("amount"),
            cll.PercentageDifferenceLevel("amount", 0.0),  # 4
            cll.PercentageDifferenceLevel("amount", (0.2 / 1.2) + 1e-4),  # 3
            cll.PercentageDifferenceLevel("amount", (0.2 / 1.0) + 1e-4),  # 2
            cll.PercentageDifferenceLevel("amount", (60 / 200) + 1e-4),  # 1
            cll.ElseLevel(),
        ],
    )

    test_cases = [
        {
            "comparison": perc_comparison,
            "inputs": [
                {
                    "amount_l": 1.2,
                    "amount_r": 1.0,
                    "expected_value": 3,
                    "expected_label": "Percentage difference of 'amount' within 16.68%",
                },
                {
                    "amount_l": 1.0,
                    "amount_r": 0.8,
                    "expected_value": 2,
                    "expected_label": "Percentage difference of 'amount' within 20.01%",
                },
                {
                    "amount_l": 200,
                    "amount_r": 140,
                    "expected_value": 1,
                    "expected_label": "Percentage difference of 'amount' within 30.01%",
                },
                {
                    "amount_l": 100,
                    "amount_r": 50,
                    "expected_value": 0,
                    "expected_label": "All other comparisons",
                },
                {
                    "amount_l": None,
                    "amount_r": 100,
                    "expected_value": -1,
                    "expected_label": "amount is NULL",
                },
            ],
        },
    ]

    run_comparison_vector_value_tests(test_cases, db_api)


@mark_with_dialects_excluding()
def test_levenshtein_level(test_helpers, dialect):
    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    levenshtein_comparison = cl.CustomComparison(
        comparison_description="name",
        comparison_levels=[
            cll.NullLevel("name"),
            cll.LevenshteinLevel("name", 0),  # 4
            cll.LevenshteinLevel("name", 1),  # 3
            cll.LevenshteinLevel("name", 2),  # 2
            cll.LevenshteinLevel("name", 3),  # 1
            cll.ElseLevel(),
        ],
    )

    test_cases = [
        {
            "comparison": levenshtein_comparison,
            "inputs": [
                {
                    "name_l": "harry",
                    "name_r": "harry",
                    "expected_value": 4,
                    "expected_label": "Levenshtein distance of name <= 0",
                },
                {
                    "name_l": "harry",
                    "name_r": "barry",
                    "expected_value": 3,
                    "expected_label": "Levenshtein distance of name <= 1",
                },
                {
                    "name_l": "harry",
                    "name_r": "gary",
                    "expected_value": 2,
                    "expected_label": "Levenshtein distance of name <= 2",
                },
                {
                    "name_l": "harry",
                    "name_r": "sally",
                    "expected_value": 1,
                    "expected_label": "Levenshtein distance of name <= 3",
                },
                {
                    "name_l": "harry",
                    "name_r": "harry12345",
                    "expected_value": 0,
                    "expected_label": "All other comparisons",
                },
                {
                    "name_l": None,
                    "name_r": "harry",
                    "expected_value": -1,
                    "expected_label": "name is NULL",
                },
            ],
        },
    ]

    run_comparison_vector_value_tests(test_cases, db_api)


# postgres has no Damerau-Levenshtein
@mark_with_dialects_excluding("postgres")
def test_damerau_levenshtein_level(test_helpers, dialect):
    helper = test_helpers[dialect]

    data = [
        {"id": 1, "name": "harry"},
        {"id": 2, "name": "harry"},
        {"id": 3, "name": "barry"},
        {"id": 4, "name": "gary"},
        {"id": 5, "name": "sally"},
        {"id": 6, "name": "sharry"},
        {"id": 7, "name": "haryr"},
        {"id": 8, "name": "ahryr"},
        {"id": 9, "name": "harry12345"},
        {"id": 10, "name": "ahrryt"},
        {"id": 11, "name": "hy"},
        {"id": 12, "name": "r"},
    ]
    # id and expected levenshtein distance from id:1 "harry"
    id_distance_from_1 = {
        2: 0,
        3: 1,
        4: 2,
        5: 3,
        6: 1,
        7: 1,
        8: 2,
        9: 5,
        10: 2,
        11: 3,
        12: 4,
    }

    settings = {
        "unique_id_column_name": "id",
        "link_type": "dedupe_only",
        "comparisons": [
            {
                "output_column_name": "name",
                "comparison_levels": [
                    cll.NullLevel("name"),
                    cll.DamerauLevenshteinLevel("name", 0),  # 4
                    cll.DamerauLevenshteinLevel("name", 1),  # 3
                    cll.DamerauLevenshteinLevel("name", 2),  # 2
                    cll.DamerauLevenshteinLevel("name", 3),  # 1
                    cll.ElseLevel(),  # 0
                ],
            },
        ],
        "retain_matching_columns": True,
        "retain_intermediate_calculation_columns": True,
    }

    def gamma_lev_from_distance(dist):
        # which gamma value will I get for a given levenshtein distance?
        if dist == 0:
            return 4
        elif dist == 1:
            return 3
        elif dist == 2:
            return 2
        elif dist == 3:
            return 1
        elif dist > 3:
            return 0
        raise ValueError(f"Invalid distance supplied ({dist})")

    df = pd.DataFrame(data)
    df = helper.convert_frame(df)

    linker = helper.Linker(df, settings, **helper.extra_linker_args())
    df_e = linker.inference.predict().as_pandas_dataframe()

    for id_r, lev_dist in id_distance_from_1.items():
        expected_gamma_lev = gamma_lev_from_distance(lev_dist)
        row = dict(df_e.query(f"id_l == 1 and id_r == {id_r}").iloc[0])
        assert row["gamma_name"] == expected_gamma_lev
