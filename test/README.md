# Shorthand Tests

Tests are written using `pytest`. If you don't have pytest installed, you can install it via:
```bash
$ pip install pytest
```

## Configuration
Depending on the paths to the utilities `grep` and `find` on your system, you may need to change the configuration which is used to run the tests. this can be done using the file `config_override.json` in this directory.

## Running tests
To run tests, you can invoke pytest as follows:
```bash
# Run all tests
$ pytest .

# Run a single test file
$ pytest <test-file>
```
