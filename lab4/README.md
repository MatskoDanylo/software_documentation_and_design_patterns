# Lab 4 - GoF Strategy Pattern (Python)

This lab demonstrates the **Strategy** design pattern with strict separation of concerns:
- `DataReader` only reads CSV data.
- `OutputStrategy` implementations control where data is written.
- Output destination is switched via `config.json` only.

## Files
- `main.py` - entry point, loads config, uses a factory to pick strategy.
- `data_reader.py` - context class that reads CSV and delegates output.
- `strategies.py` - strategy interface + concrete strategies.
- `config.json` - output selection and strategy settings.
- `requirements.txt` - optional libraries for real Kafka/Redis integration.

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Switch output without code changes
Open `config.json` and set:
- `"output_type": "console"`
- `"output_type": "file"`
- `"output_type": "kafka"`
- `"output_type": "redis"`

### Notes
- `FileOutputStrategy` supports `"format": "json"` or `"csv"`.
- Kafka and Redis strategies can run in simulation mode when infra is not available (`simulate_on_error: true`).
