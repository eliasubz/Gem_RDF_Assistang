import csv
import os


def compute_accuracy(csv_file_path):
    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = 0
        correct = 0

        for row in reader:
            if row["Column"] == "row_id":
                continue  # Skip the 'row_id' entry

            match = row.get("is match", "").strip()
            if match == "1":
                correct += 1
            total += 1

        accuracy = (correct / total) * 100 if total > 0 else 0.0
        return {
            "file": os.path.basename(csv_file_path),
            "total": total,
            "correct": correct,
            "accuracy": round(accuracy, 2),
        }


# Configurable parameters
hop_counts = [1, 2]
example_counts = [1, 3]
uri_combinations = [True, False]  # True = short, False = long
base_output_dir = (
    "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/Data/raw_data"
)

## 1. CHANGE HERE
base_experiment = "path_selection_spec_instr_"
base_experiment = "path_selection_mini_"
output_csv_path = "meta_evaluation_gpt.csv"
## 2. CHANGE HERE
output_csv_path = "meta_evaluation_mini.csv"

# Headers for the output CSV
csv_headers = [
    "Config ID",
    "Hop",
    "URI",
    "#Sample Values",
    "Strict",
    "Accuracy",
    "#Correct",
    "#Total Cases",
    "#Accuracy Administration",
    "#Acc Measurement",
    "#Acc Prescription",
]


def main():
    rows = []
    config_counter = 1

    for hop_count in hop_counts:
        for num_examples in example_counts:
            for short_uri in uri_combinations:

                uri_type = "short_URI" if short_uri else "long_URI"
                readable_uri = "Short" if short_uri else "Long"
                folder_name = (
                    f"{base_experiment}{hop_count}_hop_{uri_type}_{num_examples}_smpl"
                )
                config_path = os.path.join(base_output_dir, folder_name)

                for strict_eval in ["evaluation", "evaluation_strict"]:
                    strict_flag = "Yes" if strict_eval == "evaluation_strict" else "No"
                    eval_path = os.path.join(config_path, strict_eval)

                    admin_csv = os.path.join(eval_path, "administrative_cases.csv")
                    measure_csv = os.path.join(eval_path, "measurements.csv")
                    prescrip_csv = os.path.join(eval_path, "prescriptions.csv")

                    if not all(
                        os.path.isfile(p)
                        for p in [admin_csv, measure_csv, prescrip_csv]
                    ):

                        for p in [admin_csv, measure_csv, prescrip_csv]:
                            print(os.path.isfile(p))

                        print(f"Skipping missing data in: {admin_csv}")
                        continue

                    admin_acc = compute_accuracy(admin_csv)
                    measure_acc = compute_accuracy(measure_csv)
                    prescrip_acc = compute_accuracy(prescrip_csv)

                    total_cases = (
                        admin_acc["total"]
                        + measure_acc["total"]
                        + prescrip_acc["total"]
                    )
                    total_correct = (
                        admin_acc["correct"]
                        + measure_acc["correct"]
                        + prescrip_acc["correct"]
                    )
                    total_accuracy = (
                        round((total_correct / total_cases) * 100, 2)
                        if total_cases > 0
                        else 0.0
                    )

                    config_id = f"EXP{config_counter}"
                    config_counter += 1

                    row = [
                        config_id,
                        hop_count,
                        readable_uri,
                        num_examples,
                        strict_flag,
                        total_accuracy,
                        total_correct,
                        total_cases,
                        admin_acc["accuracy"],
                        measure_acc["accuracy"],
                        prescrip_acc["accuracy"],
                    ]
                    rows.append(row)

    rows.sort(key=lambda row: row[4], reverse=True)  # row[4] is the "Strict" column

    # Write to CSV
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(rows)

    print(f"Meta evaluation CSV written to: {output_csv_path}")


if __name__ == "__main__":
    main()
