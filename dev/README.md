# Mixture App

## Overview

The Mixture App is designed to run model comparisons using various models provided by Substrate. It loads or creates a configuration containing the Substrate API key, selects models based on the provided arguments, and runs comparisons to evaluate their performance.

## Getting Started

Before you begin, you'll need to sign up and obtain an API key from Substrate. Visit [Substrate's website](https://substrate.run) to sign up and retrieve your API key.

## Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project_directory>
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Mixture Script

The `mixture.py` script compares different models using a specified prompt. It can randomize the model selection, use all combinations of models, or use specific models provided as arguments.

```bash
python dev/mixture.py
```

#### Example Usage

1. To use randomized model selection:
   ```bash
   python dev/mixture.py --randomize
   ```

2. To use all combinations of models:
   ```bash
   python dev/mixture.py --all
   ```

3. To use specific models (3 required):
   ```bash
   python dev/mixture.py --models Mistral7BInstruct Mixtral8x7BInstruct Llama3Instruct8B
   ```

You can also specify the number of runs to perform using the `--runs` argument (default is 50):
```bash
python dev/mixture.py --randomize --runs 100
```

## Functions

### load_or_create_config
Handles the loading or creation of configuration containing the API key.

### run_comparison
Runs the comparison between selected models based on the specified prompt and logs the results.

### main
The main entry point for the script. Handles argument parsing, model selection, and initiates the comparison process.

## License

This project is licensed under the [BSD-3-Clause License](LICENSE).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct and the process for submitting pull requests.

## Authors

- **Kord Campbell** - *Initial work* - [YourGitHubProfile](https://github.com/YourGitHubProfile)

See also the list of [contributors](https://github.com/YourRepo/contributors) who participated in this project.

## Acknowledgments

- Hat tip to anyone whose code was used
- Inspiration
- etc