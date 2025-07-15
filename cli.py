import argparse
from agent.agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config
# ---------------------
# Define helper tools with top-level "name"/"description"/"parameters" as required by the
# OpenAI Responses API (same schema used in examples/).

VMWARE_HELPER_TOOLS = [
    {
        "type": "function",
        "name": "vm_activate_login_screen",
        "description": "Wake the Windows lock screen inside the powered-on VM.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "vm_login_with_password",
        "description": "Type the given password (and optional username) in the VM login box and press Enter.",
        "parameters": {
            "type": "object",
            "properties": {
                "password": {"type": "string", "description": "Windows account password"},
                "username": {"type": "string", "description": "Optional username"},
            },
            "required": ["password"],
        },
    },
    {
        "type": "function",
        "name": "vm_simple_login_flow",
        "description": "Activate the lock screen and then log in using the supplied credentials.",
        "parameters": {
            "type": "object",
            "properties": {
                "password": {"type": "string", "description": "Windows account password"},
                "username": {"type": "string", "description": "Optional username"},
            },
            "required": ["password"],
        },
    },
    {
        "type": "function",
        "name": "vm_try_wake_screen",
        "description": "Try various keypresses/clicks to wake an unresponsive lock screen.",
        "parameters": {"type": "object", "properties": {}},
    },
]
# ---------------------


def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.lower().strip() == "y"


def main():
    parser = argparse.ArgumentParser(
        description="Select a computer environment from the available options."
    )
    parser.add_argument(
        "--computer",
        choices=computers_config.keys(),
        help="Choose the computer environment to use.",
        default="local-playwright",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Initial input to use instead of asking the user.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show images during the execution.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        help="Start the browsing session with a specific URL (only for browser environments).",
        default="https://bing.com",
    )
    args = parser.parse_args()
    ComputerClass = computers_config[args.computer]

    # Choose helper tools only when using the Windows desktop computer.
    with ComputerClass() as computer:
        extra_tools = VMWARE_HELPER_TOOLS if args.computer == "windows-desktop" else []
        agent = Agent(
            computer=computer,
            tools=extra_tools,
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )
        # Prepend a system message to steer the agent's behaviour
        if args.computer == "windows-desktop":
            # Use built-in VMware automation prompt for Windows desktop
            system_content = computer.SYSTEM_PROMPT
        else:
            # Default system message for other computer types
            system_content = (
                "You are a computer use agent helping automate desktop applications. "
                "Be precise and ask for confirmation before important actions."
            )
        
        items = [
            {
                "role": "system",
                "content": system_content,
            }
        ]

        if args.computer in ["browserbase", "local-playwright"]:
            if not args.start_url.startswith("http"):
                args.start_url = "https://" + args.start_url
            if hasattr(agent.computer, 'goto'):
                agent.computer.goto(args.start_url)  # type: ignore[attr-defined]

        while True:
            try:
                user_input = args.input or input("> ")
                if user_input == "exit":
                    break
            except EOFError as e:
                print(f"An error occurred: {e}")
                break
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(
                items,
                print_steps=True,
                show_images=args.show,
                debug=args.debug,
            )
            items += output_items
            args.input = None


if __name__ == "__main__":
    main()
