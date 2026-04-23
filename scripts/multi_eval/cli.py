import argparse
from .prompts import CATEGORIES
from .config import MODELS, JUDGE_MODEL


def main():
    parser = argparse.ArgumentParser(
        prog="python -m multi_eval",
        description="ARIA Multi-Model Adversarial Evaluation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full run — all models, all categories
  python -m multi_eval run

  # Targeted run — prompt hacking and harmful request only
  python -m multi_eval run --categories PH HR

  # Specific models only
  python -m multi_eval run --models mistral:latest smollm2:latest llama3.1:8b

  # Custom judge model
  python -m multi_eval run --judge llama3.1:8b --notes "llama as judge baseline"

  # Report on the latest run
  python -m multi_eval report

  # Report on a specific run
  python -m multi_eval report --run-id <uuid>

  # Manual scoring — conflicts first, then critical severity
  python -m multi_eval review --run-id <uuid>

  # Manual scoring filtered to one category
  python -m multi_eval review --run-id <uuid> --category META

  # List configured models
  python -m multi_eval models
""",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── run ──────────────────────────────────────────────────────────────────
    run_p = sub.add_parser("run", help="Run the evaluation matrix")
    run_p.add_argument(
        "--categories", nargs="+", choices=CATEGORIES, metavar="CAT",
        help=f"Categories to test. Choices: {', '.join(CATEGORIES)} (default: all)",
    )
    run_p.add_argument(
        "--models", nargs="+", metavar="MODEL",
        help="Model names to test (default: all configured in config.py)",
    )
    run_p.add_argument(
        "--judge", default=JUDGE_MODEL, metavar="MODEL",
        help=f"Judge model for LLM-as-evaluator scoring (default: {JUDGE_MODEL})",
    )
    run_p.add_argument(
        "--notes", default="", metavar="TEXT",
        help="Optional notes stored with the run record",
    )
    run_p.add_argument(
        "--db", default=None, metavar="PATH",
        help="Override SQLite database path",
    )

    # ── report ───────────────────────────────────────────────────────────────
    rep_p = sub.add_parser("report", help="Print summary report")
    rep_p.add_argument("--run-id", default=None, metavar="UUID",
                       help="Run ID to report on (default: most recent)")
    rep_p.add_argument("--db", default=None, metavar="PATH")

    # ── review ───────────────────────────────────────────────────────────────
    rev_p = sub.add_parser("review", help="Interactive manual scoring session")
    rev_p.add_argument("--run-id", required=True, metavar="UUID")
    rev_p.add_argument("--category", choices=CATEGORIES, default=None, metavar="CAT",
                       help="Filter review to one category")
    rev_p.add_argument("--db", default=None, metavar="PATH")

    # ── models ───────────────────────────────────────────────────────────────
    sub.add_parser("models", help="List configured models")

    args = parser.parse_args()

    if args.command == "run":
        from .runner import run_eval
        run_eval(
            categories=args.categories,
            models=args.models,
            judge_model=args.judge,
            notes=args.notes,
            db_path=args.db,
        )

    elif args.command == "report":
        from .report import print_summary
        print_summary(run_id=args.run_id, db_path=args.db)

    elif args.command == "review":
        from .review import manual_review
        manual_review(run_id=args.run_id, category=args.category, db_path=args.db)

    elif args.command == "models":
        print(f"\n{'Name':<28} {'Family':<10} {'GB':>5} {'Coder'}")
        print("-" * 55)
        for m in MODELS:
            print(f"{m['name']:<28} {m['family']:<10} {m['size_gb']:>5.1f} {'yes' if m['is_coder'] else 'no'}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
