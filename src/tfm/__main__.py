from .tfm_bot import TFMBot


def main() -> None:
    bot: TFMBot = TFMBot()
    bot()


if __name__ == "__main__":
    main()
