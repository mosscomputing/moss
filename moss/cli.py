import argparse
import json
import sys
from . import Subject, Envelope


def main():
    parser = argparse.ArgumentParser(prog="moss", description="MOSS CLI - Sign and verify agent outputs")
    subparsers = parser.add_subparsers(dest="command")

    # moss subject create <subject>
    sub_parser = subparsers.add_parser("subject", help="Manage subjects")
    sub_sub = sub_parser.add_subparsers(dest="subcommand")
    create_parser = sub_sub.add_parser("create", help="Create new subject")
    create_parser.add_argument("subject", help="Subject ID (moss:namespace:name)")

    # moss sign <subject> <payload_file>
    sign_parser = subparsers.add_parser("sign", help="Sign a payload")
    sign_parser.add_argument("subject", help="Subject to sign as")
    sign_parser.add_argument("payload_file", help="JSON payload file (- for stdin)")

    # moss verify <payload_file> <envelope_file>
    verify_parser = subparsers.add_parser("verify", help="Verify an envelope")
    verify_parser.add_argument("payload_file", help="JSON payload file")
    verify_parser.add_argument("envelope_file", help="Envelope JSON file")
    verify_parser.add_argument("--no-replay-check", action="store_true", help="Skip replay detection")

    # moss diff <env1> <env2>
    diff_parser = subparsers.add_parser("diff", help="Compare two envelopes")
    diff_parser.add_argument("envelope1", help="First envelope file")
    diff_parser.add_argument("envelope2", help="Second envelope file")

    args = parser.parse_args()

    try:
        if args.command == "subject" and args.subcommand == "create":
            subject = Subject.create(args.subject)
            print(f"Created: {args.subject}")
            print(f"  Public key: {subject.public_key.hex()[:32]}...")
            sys.exit(0)

        elif args.command == "sign":
            subject = Subject.load(args.subject)
            if args.payload_file == "-":
                payload = json.load(sys.stdin)
            else:
                with open(args.payload_file) as f:
                    payload = json.load(f)
            envelope = subject.sign(payload)
            print(json.dumps(envelope.to_dict(), indent=2))
            sys.exit(0)

        elif args.command == "verify":
            with open(args.payload_file) as f:
                payload = json.load(f)
            with open(args.envelope_file) as f:
                envelope_data = json.load(f)
            envelope = Envelope.from_dict(envelope_data)
            result = Subject.verify(
                envelope,
                payload,
                check_replay=not args.no_replay_check
            )
            if result.valid:
                print(f"Valid signature from {result.subject}")
                sys.exit(0)
            else:
                print(f"Invalid: {result.reason} [{result.error_code}]")
                sys.exit(1)

        elif args.command == "diff":
            with open(args.envelope1) as f:
                env1 = json.load(f)
            with open(args.envelope2) as f:
                env2 = json.load(f)

            diffs = []
            all_keys = set(env1.keys()) | set(env2.keys())
            for key in sorted(all_keys):
                v1 = env1.get(key)
                v2 = env2.get(key)
                if v1 != v2:
                    diffs.append(f"  {key}: {v1} -> {v2}")

            if diffs:
                print("Differences:")
                print("\n".join(diffs))
            else:
                print("Envelopes are identical")
            sys.exit(0)

        else:
            parser.print_help()
            sys.exit(3)

    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        code = getattr(e, 'code', 'MOSS_ERR_000')
        print(f"{e} [{code}]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
