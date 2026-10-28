import subprocess
import sys
import time

STEPS = [
    ("Parse matches", "data_module.load_matches", False),
    ("Clean venues", "data_module.clean_venues", False),
    ("Parse deliveries", "data_module.load_deliveries", False),
    ("Build innings summary", "data_module.build_innings_summary", False),
    ("Find ground coordinates", "data_module.build_venue_coords", True),
    ("Fetch weather", "data_module.build_weather", True),
    ("Build match features", "data_module.build_match_features", False),
    ("Make training data", "ml.make_training_data", False),
    ("Train model", "ml.train_model_v2", False),
]


def main():
    skip_network = "--skip-network" in sys.argv
    start = time.time()
    for name, module, needs_network in STEPS:
        if skip_network and needs_network:
            print(f"--- Skipping: {name} (needs internet)")
            continue
        print(f"--- {name}")
        result = subprocess.run([sys.executable, "-m", module])
        if result.returncode != 0:
            print(f"FAILED at step: {name}")
            sys.exit(result.returncode)
    print(f"Pipeline finished in {round(time.time() - start)} seconds")


if __name__ == "__main__":
    main()
