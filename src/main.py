from agent_demo import parse_args, run_agent


def main():
    args = parse_args()
    run_agent(
        input_path=args.input,
        rules_path=args.rules,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
