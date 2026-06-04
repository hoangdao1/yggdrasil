"""Tests for multimodal image query and visual RAG support."""

from __future__ import annotations

import base64
import os
import tempfile

import pytest

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.media import (
    build_query,
    image_from_base64,
    image_from_file,
    image_from_url,
)
from yggdrasil_lm.testing import StubBackend, end_turn


# ---------------------------------------------------------------------------
# media.py helpers
# ---------------------------------------------------------------------------

class TestImageHelpers:
    def test_image_from_url(self):
        block = image_from_url("https://example.com/img.png")
        assert block == {"type": "image", "source": {"type": "url", "url": "https://example.com/img.png"}}

    def test_image_from_base64(self):
        block = image_from_base64("abc123", "image/png")
        assert block == {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": "abc123"},
        }

    def test_image_from_base64_default_media_type(self):
        block = image_from_base64("data")
        assert block["source"]["media_type"] == "image/jpeg"

    def test_image_from_file_png(self):
        raw = b"\x89PNG\r\n\x1a\n"  # PNG magic bytes
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(raw)
            f.flush()
            block = image_from_file(f.name)
        os.unlink(f.name)
        assert block["type"] == "image"
        assert block["source"]["type"] == "base64"
        assert block["source"]["media_type"] == "image/png"
        assert block["source"]["data"] == base64.standard_b64encode(raw).decode()

    def test_image_from_file_explicit_media_type(self):
        raw = b"data"
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(raw)
            f.flush()
            block = image_from_file(f.name, media_type="image/webp")
        os.unlink(f.name)
        assert block["source"]["media_type"] == "image/webp"

    def test_build_query_no_images_returns_str(self):
        result = build_query("Hello")
        assert result == "Hello"

    def test_build_query_with_images_returns_list(self):
        img = image_from_url("https://example.com/a.jpg")
        result = build_query("Describe this.", img)
        assert isinstance(result, list)
        assert result[0] == {"type": "text", "text": "Describe this."}
        assert result[1] == img

    def test_build_query_multiple_images(self):
        img1 = image_from_url("https://example.com/a.jpg")
        img2 = image_from_url("https://example.com/b.jpg")
        result = build_query("Compare these.", img1, img2)
        assert len(result) == 3
        assert result[0]["type"] == "text"
        assert result[1] == img1
        assert result[2] == img2


# ---------------------------------------------------------------------------
# GraphApp.add_image_context
# ---------------------------------------------------------------------------

class TestAddImageContext:
    @pytest.mark.asyncio
    async def test_url_context_node(self):
        app = GraphApp(backend=StubBackend([end_turn("ok")]))
        node = await app.add_image_context("Logo", url="https://example.com/logo.png")
        assert node.content_type == "image"
        assert node.content == "https://example.com/logo.png"
        assert node.attributes["image_source"] == "url"

    @pytest.mark.asyncio
    async def test_base64_context_node(self):
        app = GraphApp(backend=StubBackend([end_turn("ok")]))
        node = await app.add_image_context("Diagram", data="abc123", media_type="image/png")
        assert node.content_type == "image"
        assert node.content == "abc123"
        assert node.attributes["image_source"] == "base64"
        assert node.attributes["media_type"] == "image/png"

    @pytest.mark.asyncio
    async def test_file_context_node(self):
        raw = b"\x89PNG\r\n"
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(raw)
            f.flush()
            app = GraphApp(backend=StubBackend([end_turn("ok")]))
            node = await app.add_image_context("Photo", path=f.name)
        os.unlink(f.name)
        assert node.content_type == "image"
        assert node.attributes["image_source"] == "base64"
        assert node.attributes["media_type"] == "image/png"
        assert node.content == base64.standard_b64encode(raw).decode()

    @pytest.mark.asyncio
    async def test_requires_exactly_one_source(self):
        app = GraphApp(backend=StubBackend([end_turn("ok")]))
        with pytest.raises(ValueError):
            await app.add_image_context("Bad", url="https://x.com/a.jpg", data="abc")

    @pytest.mark.asyncio
    async def test_requires_at_least_one_source(self):
        app = GraphApp(backend=StubBackend([end_turn("ok")]))
        with pytest.raises(ValueError):
            await app.add_image_context("Empty")


# ---------------------------------------------------------------------------
# Multimodal query — end-to-end with StubBackend
# ---------------------------------------------------------------------------

class TestMultimodalQuery:
    @pytest.mark.asyncio
    async def test_list_query_reaches_backend(self):
        backend = StubBackend([end_turn("A cat.")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Vision", system_prompt="Describe images.")

        query = build_query("What is this?", image_from_url("https://example.com/cat.jpg"))
        ctx = await app.run(agent, query)

        assert ctx.outputs[agent.node_id]["text"] == "A cat."
        # The backend should have received a list-typed content in the user message
        # backend.calls entries are (model, system, messages, tools) tuples
        _model, _system, messages, _tools = backend.calls[0]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert isinstance(user_msg["content"], list)
        text_block = user_msg["content"][0]
        image_block = user_msg["content"][1]
        assert text_block == {"type": "text", "text": "What is this?"}
        assert image_block["type"] == "image"

    @pytest.mark.asyncio
    async def test_string_query_still_works(self):
        backend = StubBackend([end_turn("Hello!")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Bot", system_prompt="You are helpful.")
        ctx = await app.run(agent, "Hi")
        assert ctx.outputs[agent.node_id]["text"] == "Hello!"


# ---------------------------------------------------------------------------
# Visual RAG — image ContextNode injected into user message
# ---------------------------------------------------------------------------

class TestVisualRAG:
    @pytest.mark.asyncio
    async def test_image_context_injected_into_user_message(self):
        backend = StubBackend([end_turn("A red logo.")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Analyst", system_prompt="Analyse images.")
        img_ctx = await app.add_image_context("Logo", url="https://cdn.example.com/logo.png")
        await app.connect_context(agent, img_ctx)

        ctx = await app.run(agent, "What colour is the logo?")

        _model, _system, messages, _tools = backend.calls[0]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert isinstance(user_msg["content"], list), "user message must be multimodal"
        text_block = next(b for b in user_msg["content"] if b.get("type") == "text")
        image_block = next(b for b in user_msg["content"] if b.get("type") == "image")
        assert text_block["text"] == "What colour is the logo?"
        assert image_block["source"]["url"] == "https://cdn.example.com/logo.png"

    @pytest.mark.asyncio
    async def test_image_context_not_in_system_prompt(self):
        backend = StubBackend([end_turn("ok")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Bot", system_prompt="You are helpful.")
        img_ctx = await app.add_image_context("Chart", url="https://example.com/chart.png")
        await app.connect_context(agent, img_ctx)

        await app.run(agent, "Describe the chart.")

        _model, system, _messages, _tools = backend.calls[0]
        assert "https://example.com/chart.png" not in system

    @pytest.mark.asyncio
    async def test_multimodal_query_plus_image_context_merged(self):
        backend = StubBackend([end_turn("Both noted.")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Vision", system_prompt="You see images.")
        img_ctx = await app.add_image_context("Background", url="https://example.com/bg.jpg")
        await app.connect_context(agent, img_ctx)

        inline_img = image_from_url("https://example.com/fg.jpg")
        query = build_query("Compare these.", inline_img)
        await app.run(agent, query)

        _model, _system, messages, _tools = backend.calls[0]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert isinstance(user_msg["content"], list)
        image_blocks = [b for b in user_msg["content"] if b.get("type") == "image"]
        assert len(image_blocks) == 2

    @pytest.mark.asyncio
    async def test_text_context_still_in_system_prompt(self):
        backend = StubBackend([end_turn("ok")])
        app = GraphApp(backend=backend)
        agent = await app.add_agent("Bot", system_prompt="You are helpful.")
        txt_ctx = await app.add_context("Policy", "Always be polite.")
        img_ctx = await app.add_image_context("Chart", url="https://example.com/chart.png")
        await app.connect_context(agent, txt_ctx)
        await app.connect_context(agent, img_ctx)

        await app.run(agent, "Describe the chart.")

        _model, system, _messages, _tools = backend.calls[0]
        assert "Always be polite." in system
        assert "https://example.com/chart.png" not in system
