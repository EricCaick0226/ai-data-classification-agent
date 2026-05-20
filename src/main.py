from agent_runner import parse_args, resolve_paths, run_agent


def main():
    args = parse_args()
    input_path, rules_path, output_path = resolve_paths(args)
    run_agent(
        input_path=input_path,
        rules_path=rules_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
