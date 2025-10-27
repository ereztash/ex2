#!/usr/bin/env python3
"""
MakeGPT CLI - Command Line Interface

This is the user-facing entry point for the MakeGPT compiler.

Usage:
    # Generate blueprint only
    python -m src.main "Send email when form submitted"

    # Generate and deploy to Make.com
    python -m src.main "Send email when form submitted" --deploy --team-id 123 --folder-id 456

    # Save blueprint to file
    python -m src.main "Send email when form submitted" --output blueprint.json

Architecture: This CLI orchestrates the 3-stage pipeline:
    Intent → Plan → Synthesis → [Optional: Deploy]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import MakeGPT
from src.encoder import Base64Encoder
from src.make_api import MakeAPIError
from src.schema_validator import ValidationError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MakeGPT - AI-powered Make.com scenario compiler",
        epilog="""
Examples:
  # Generate blueprint
  python -m src.main "Send email when new form is submitted"

  # Deploy to Make.com
  python -m src.main "Create calendar event from Slack message" \\
      --deploy --team-id 12345 --folder-id 67890

  # Save to file
  python -m src.main "Update spreadsheet from webhook" \\
      --output my-scenario.json
        """
    )

    parser.add_argument(
        "intent",
        type=str,
        help="Natural language description of the automation you want to create"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save blueprint to JSON file"
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy blueprint to Make.com after generation"
    )

    parser.add_argument(
        "--team-id",
        type=int,
        help="Make.com team ID (required for --deploy)"
    )

    parser.add_argument(
        "--folder-id",
        type=int,
        help="Make.com folder ID (required for --deploy)"
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Custom scenario name (optional)"
    )

    parser.add_argument(
        "--base64",
        action="store_true",
        help="Also output Base64-encoded blueprint"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress information"
    )

    args = parser.parse_args()

    # Validate deployment arguments
    if args.deploy and (args.team_id is None or args.folder_id is None):
        parser.error("--deploy requires --team-id and --folder-id")

    try:
        # Initialize compiler
        if args.verbose:
            print("Initializing MakeGPT compiler...")

        compiler = MakeGPT(
            openai_key=os.getenv("OPENAI_API_KEY"),
            make_token=os.getenv("MAKE_API_TOKEN") if args.deploy else None
        )

        # Stage 1-3: Compile intent to blueprint
        print(f"\nCompiling automation: \"{args.intent}\"")
        print("=" * 60)

        if args.verbose:
            print("\n[Stage 1/3] Analyzing intent...")

        blueprint = compiler.compile(args.intent)

        if args.verbose:
            print("[Stage 2/3] Planning scenario...")
            print("[Stage 3/3] Synthesizing blueprint...")

        print("\n✓ Blueprint generated successfully!")
        print(f"  Scenario name: {blueprint.get('name', 'Unnamed')}")
        print(f"  Modules: {len(blueprint.get('flow', []))}")

        # Display blueprint
        print("\n" + "=" * 60)
        print("BLUEPRINT JSON:")
        print("=" * 60)
        print(json.dumps(blueprint, indent=2, ensure_ascii=False))

        # Base64 encoding
        if args.base64 or args.deploy:
            encoder = Base64Encoder()
            blueprint_b64 = encoder.encode(blueprint)

            if args.base64:
                print("\n" + "=" * 60)
                print("BASE64 ENCODED (for API):")
                print("=" * 60)
                print(blueprint_b64)

        # Save to file
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Saved to: {args.output}")

        # Deploy to Make.com
        if args.deploy:
            print("\n" + "=" * 60)
            print("DEPLOYING TO MAKE.COM")
            print("=" * 60)

            scenario_id = compiler.deploy(
                blueprint=blueprint,
                team_id=args.team_id,
                folder_id=args.folder_id,
                scenario_name=args.name
            )

            print(f"\n✓ Scenario created successfully!")
            print(f"  Scenario ID: {scenario_id}")
            print(f"  URL: https://eu1.make.com/scenarios/{scenario_id}/edit")

            print("\n" + "!" * 60)
            print("IMPORTANT: Human-in-the-Loop Required")
            print("!" * 60)
            print("""
This scenario has been created but is UNLINKED.

You must now:
1. Open the scenario in Make.com (URL above)
2. Click on each module with a connection warning
3. Select your connected account for each service
4. Save the scenario

This manual linking step is required for security reasons.
Make.com does not allow programmatic connection of user accounts.
            """)

        return 0

    except ValidationError as e:
        print(f"\n✗ Blueprint validation failed:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return 1

    except MakeAPIError as e:
        print(f"\n✗ Make.com API error:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error:", file=sys.stderr)
        print(f"  {type(e).__name__}: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
