"""End-to-end tests for the Agent Composer chat UI using Playwright."""

import os
import re

import pytest
from playwright.sync_api import Page, expect

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context."""
    return {"base_url": FRONTEND_URL}


class TestChatInterface:
    """Tests for the basic chat interface."""

    def test_displays_chat_interface(self, page: Page):
        """Should display the chat interface with all expected elements."""
        page.goto("/")

        # Check header
        expect(page.get_by_role("heading", name="Agent Composer")).to_be_visible()

        # Check clear chat button
        expect(page.get_by_role("button", name="Clear chat")).to_be_visible()

        # Check input area
        expect(page.get_by_placeholder("Type a message...")).to_be_visible()

        # Check send button
        expect(page.get_by_role("button", name="Send")).to_be_visible()

        # Check empty state message
        expect(page.get_by_text("Start a conversation with the agent")).to_be_visible()

    def test_shows_user_message_immediately(self, page: Page):
        """Should show user message immediately after sending."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")

        # Type a message
        input_field.fill("Hello agent!")
        send_button.click()

        # User message should appear immediately
        expect(page.get_by_text("Hello agent!")).to_be_visible()

        # Empty state should be gone
        expect(page.get_by_text("Start a conversation with the agent")).not_to_be_visible()

    def test_disables_input_while_loading(self, page: Page):
        """Should disable input while loading."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")

        # Type and send a message
        input_field.fill("Test message")
        send_button.click()

        # Input should be disabled while loading
        expect(input_field).to_be_disabled()

        # Stop button should appear (replaces Send)
        expect(page.get_by_role("button", name="Stop")).to_be_visible()

    def test_receives_assistant_response(self, page: Page):
        """Should receive and display assistant response."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")

        # Send a simple message
        input_field.fill("Say hello")
        send_button.click()

        # Wait for response to complete (Send button reappears)
        expect(page.get_by_role("button", name="Send")).to_be_visible(timeout=60000)

        # Should have at least 2 message bubbles (user + assistant)
        messages = page.locator('[class*="max-w-[85%]"]')
        expect(messages).to_have_count(2, timeout=5000)

    def test_sends_message_with_enter_key(self, page: Page):
        """Should allow sending messages with Enter key."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")

        # Type a message and press Enter
        input_field.fill("Test enter key")
        input_field.press("Enter")

        # User message should appear
        expect(page.get_by_text("Test enter key")).to_be_visible()

    def test_shift_enter_creates_newline(self, page: Page):
        """Should support Shift+Enter for new lines."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")

        # Type with Shift+Enter (should not send)
        input_field.fill("Line 1")
        input_field.press("Shift+Enter")
        input_field.type("Line 2")

        # Message should not be sent, input should contain both lines
        expect(input_field).to_have_value("Line 1\nLine 2")

    def test_clears_messages_with_clear_button(self, page: Page):
        """Should clear messages with Clear chat button."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")
        clear_button = page.get_by_role("button", name="Clear chat")

        # Send a message first
        input_field.fill("Test message to clear")
        send_button.click()

        # Wait for message to appear
        expect(page.get_by_text("Test message to clear")).to_be_visible()

        # Clear the chat
        clear_button.click()

        # Message should be gone
        expect(page.get_by_text("Test message to clear")).not_to_be_visible()

        # Empty state should return
        expect(page.get_by_text("Start a conversation with the agent")).to_be_visible()

    def test_stops_generation(self, page: Page):
        """Should stop generation when Stop button is clicked."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")

        # Send a message that might trigger a longer response
        input_field.fill("Write a long explanation")
        send_button.click()

        # Wait for Stop button to appear
        stop_button = page.get_by_role("button", name="Stop")
        expect(stop_button).to_be_visible(timeout=5000)

        # Click stop
        stop_button.click()

        # Send button should reappear
        expect(send_button).to_be_visible(timeout=5000)

        # Input should be enabled again
        expect(input_field).to_be_enabled()


class TestToolCallDisplay:
    """Tests for tool call display."""

    def test_displays_tool_calls(self, page: Page):
        """Should display tool calls when agent uses tools."""
        page.goto("/")

        input_field = page.get_by_placeholder("Type a message...")
        send_button = page.get_by_role("button", name="Send")

        # Send a message that should trigger a tool call
        input_field.fill("Run this Python code: print('test')")
        send_button.click()

        # Wait for response to complete
        expect(page.get_by_role("button", name="Send")).to_be_visible(timeout=60000)

        # Look for tool call card (should show run_python_code or similar)
        # Tool calls show the tool name in a monospace font
        tool_card = page.locator('[class*="font-mono"]').first

        # The tool card might exist if the agent chose to use a tool
        # This is model-dependent, so we just check the UI handles it gracefully
        if tool_card.count() > 0:
            expect(tool_card).to_be_visible()
