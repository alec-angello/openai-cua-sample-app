import argparse
import json
from agent.agent import Agent
from utils import show_image, check_blocklisted_url
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


class VMwareAwareAgent(Agent):
    """Extended Agent that properly handles VMware helper functions."""

    def handle_item(self, item):
        """Enhanced item handler for VMware functions."""
        if item["type"] == "message":
            if self.print_steps:
                print(item["content"][0]["text"])

        if item["type"] == "function_call":
            name, args = item["name"], json.loads(item["arguments"])
            if self.print_steps:
                print(f"Calling VMware helper: {name}({args})")

            # Handle VMware helper functions
            if hasattr(self.computer, name):
                method = getattr(self.computer, name)
                try:
                    result = method(**args)
                    success_msg = f"{name} completed successfully"
                    if isinstance(result, bool):
                        success_msg += f" (returned: {result})"
                    print(success_msg)
                    return [
                        {
                            "type": "function_call_output",
                            "call_id": item["call_id"],
                            "output": f"Success: {name} completed. Result: {result}",
                        }
                    ]
                except Exception as e:
                    error_msg = f"{name} failed: {str(e)}"
                    print(error_msg)
                    return [
                        {
                            "type": "function_call_output",
                            "call_id": item["call_id"],
                            "output": f"Error: {error_msg}",
                        }
                    ]
            else:
                print(f"Function {name} not found on computer")
                return [
                    {
                        "type": "function_call_output",
                        "call_id": item["call_id"],
                        "output": f"Function {name} not available",
                    }
                ]

        if item["type"] == "computer_call":
            action = item["action"]
            action_type = action["type"]
            action_args = {k: v for k, v in action.items() if k != "type"}
            if self.print_steps:
                print(f"Computer action: {action_type}({action_args})")

            method = getattr(self.computer, action_type)
            method(**action_args)

            screenshot_base64 = self.computer.screenshot()
            if self.show_images:
                show_image(screenshot_base64)

            # if user doesn't ack all safety checks exit with error
            pending_checks = item.get("pending_safety_checks", [])
            for check in pending_checks:
                message = check["message"]
                if not self.acknowledge_safety_check_callback(message):
                    raise ValueError(
                        f"Safety check failed: {message}. Cannot continue with unacknowledged safety checks."
                    )

            call_output = {
                "type": "computer_call_output",
                "call_id": item["call_id"],
                "acknowledged_safety_checks": pending_checks,
                "output": {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{screenshot_base64}",
                },
            }

            # additional URL safety checks for browser environments
            if self.computer.get_environment() == "browser":
                current_url = self.computer.get_current_url()
                check_blocklisted_url(current_url)
                call_output["output"]["current_url"] = current_url

            return [call_output]
        return []


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

    # Enhanced VMware helper tools with proper function definitions
    VMWARE_HELPER_TOOLS = [
        {
            "type": "function",
            "name": "vm_activate_login_screen",
            "description": "Wake the Windows lock screen inside the VM with a single click. Use this FIRST when you see a Windows lock screen in the VM.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "type": "function",
            "name": "vm_login_with_password",
            "description": "Enter password and login to the VM. Use ONLY AFTER vm_activate_login_screen() has been called.",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "Windows account password"},
                    "username": {"type": "string", "description": "Optional username if needed"},
                },
                "required": ["password"],
            },
        },
        {
            "type": "function",
            "name": "vm_simple_login_flow",
            "description": "Complete login flow: activate screen + enter credentials. Use when you want to do both steps at once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "Windows account password"},
                    "username": {"type": "string", "description": "Optional username if needed"},
                },
                "required": ["password"],
            },
        },
        {
            "type": "function",
            "name": "vm_try_wake_screen",
            "description": "Try various keypresses/clicks to wake an unresponsive lock screen. Use if vm_activate_login_screen doesn't work.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    ]

    with ComputerClass() as computer:
        # Use enhanced agent for VMware environments
        if args.computer == "windows-desktop":
            agent = VMwareAwareAgent(
                computer=computer,
                tools=VMWARE_HELPER_TOOLS,
                acknowledge_safety_check_callback=acknowledge_safety_check_callback,
            )
        else:
            agent = Agent(
                computer=computer,
                tools=[],
                acknowledge_safety_check_callback=acknowledge_safety_check_callback,
            )

        # System prompt
        system_content = computer.SYSTEM_PROMPT if args.computer == "windows-desktop" else (
            "You are a computer use agent helping automate desktop applications. "
            "Be precise and ask for confirmation before important actions."
        )

        items = [{"role": "system", "content": system_content}]

        if args.computer in ["browserbase", "local-playwright"]:
            if not args.start_url.startswith("http"):
                args.start_url = "https://" + args.start_url
            if hasattr(agent.computer, "goto"):
                agent.computer.goto(args.start_url)  # type: ignore[attr-defined]

        print("Enhanced VMware Desktop Automation Ready!")
        print("=" * 50)
        if args.computer == "windows-desktop":
            print("VMware Helper Functions Available:")
            print("  - vm_activate_login_screen() - Wake VM login screen")
            print("  - vm_login_with_password() - Enter credentials")
            print("  - vm_simple_login_flow() - Complete login process")
            print("  - vm_try_wake_screen() - Wake unresponsive screen")
            print("=" * 50)

        while True:
            try:
                user_input = args.input or input("> ")
                if user_input.strip().lower() == "exit":
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
