import asyncio
import base64
from uuid import uuid4

from .svg import make_svg

BUSY = {'searching', 'waiting_confirmation', 'generating_image', 'streaming_reply'}


async def run_agent(session, turn_id, text):
    tool = 'search'
    try:
        await asyncio.sleep(1.5)
        async with session.condition:
            session.emit('tool_finished', turn_id, {'tool': 'search', 'status': 'done', 'result': ['A fictional result about ' + text]})
            session.state = 'waiting_confirmation'
            session.confirmation_id = str(uuid4())
            session.confirmation = asyncio.get_running_loop().create_future()
            prompt = 'Illustration inspired by: ' + text
            session.emit('confirmation_required', turn_id, {'confirmationId': session.confirmation_id, 'prompt': prompt})
            confirmation = session.confirmation
        decision, final_prompt = await confirmation
        if decision == 'reject':
            async with session.condition:
                session.state = 'rejected'
                session.emit('turn_ended', turn_id, {'reason': 'rejected'})
            return
        async with session.condition:
            session.state = 'generating_image'
            tool = 'generate_image'
            fail = session.fail_next
            session.fail_next = False
            session.emit('tool_started', turn_id, {'tool': tool, 'status': 'in_progress'})
        await asyncio.sleep(4)
        async with session.condition:
            if fail:
                session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'failed', 'error': 'Simulated image generation failure'})
                session.state = 'failed'
                session.emit('turn_ended', turn_id, {'reason': 'failed'})
                return
            svg = make_svg(final_prompt)
            url = 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()
            session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'done', 'result': url})
            session.emit('image_generated', turn_id, {'imageUrl': url, 'prompt': final_prompt})
            session.state = 'streaming_reply'
            tool = None
        for character in 'Your image is ready. The illustration uses the approved prompt.':
            async with session.condition:
                session.emit('text_delta', turn_id, {'delta': character})
            await asyncio.sleep(0.08)
        async with session.condition:
            session.state = 'completed'
            session.emit('turn_ended', turn_id, {'reason': 'completed'})
    except asyncio.CancelledError:
        async with session.condition:
            if session.state in BUSY:
                if tool and session.state in {'searching', 'generating_image'}:
                    session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'cancelled'})
                session.state = 'cancelled'
                session.emit('turn_ended', turn_id, {'reason': 'cancelled'})
        raise
    except Exception:
        async with session.condition:
            if session.state in BUSY:
                if tool:
                    session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'failed', 'error': 'Agent execution failed'})
                session.state = 'failed'
                session.emit('turn_ended', turn_id, {'reason': 'failed'})
