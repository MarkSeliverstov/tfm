# TFM - Telegram Finance Manager

TFM is a Telegram bot that helps you manage your finances. The main feature is
to **convert your voice messages into transactions using OpenAI's Speech-to-Text
API.**

#### Why?

Because it's just faster and easier to say "I spent 10 dollars on lunch" than to type it.

#### Commands

- `/start` - Start the bot
- `/help` - Show help messages
- `/get_transactions_types` - get transactions types
- `/change_transactions_types` - change transactions types (write types separated by new line)
- `balance` - Show your current balance
- `transactions` - Show your transactions

#### Environment Variables

```bash
export BOT_TOKEN=""
export OPENAI_API_KEY=""
export DATABASE_DSN=""
```

## Development

<details>

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run tfm
```

## Testing

```bash
pytest -c pyproject.toml
```

## Formatting

```bash
poetry run poe format-code
```

</details>
