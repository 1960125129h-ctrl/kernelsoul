"""
Kernelsoul - Context System & Event Bus
Decouples modules via publish-subscribe. Foundation for Gradio UI.
"""
from typing import Callable, Dict, List, Any


class EventBus:
    """Lightweight publish-subscribe event bus."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._once_subscribers: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable) -> Callable:
        """Subscribe to event. Returns unsubscribe function."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)
        return lambda: self._unsubscribe(event, callback)

    def once(self, event: str, callback: Callable):
        """Subscribe to event for one invocation only."""
        if event not in self._once_subscribers:
            self._once_subscribers[event] = []
        self._once_subscribers[event].append(callback)

    def emit(self, event: str, data: Any = None):
        """Emit event to all subscribers. Errors are caught per-callback."""
        for cb in self._subscribers.get(event, []):
            try:
                cb(data)
            except Exception as e:
                print(f'[EventBus] {event} handler error: {e}')

        for cb in self._once_subscribers.get(event, []):
            try:
                cb(data)
            except Exception as e:
                print(f'[EventBus] {event} once handler error: {e}')
        self._once_subscribers.pop(event, None)

    def off(self, event: str):
        """Remove all subscribers for an event."""
        self._subscribers.pop(event, None)
        self._once_subscribers.pop(event, None)

    def _unsubscribe(self, event: str, callback: Callable):
        if event in self._subscribers and callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)

    def subscriber_count(self, event: str = None) -> int:
        if event:
            return len(self._subscribers.get(event, [])) + len(self._once_subscribers.get(event, []))
        return sum(len(v) for v in self._subscribers.values()) + sum(len(v) for v in self._once_subscribers.values())


# Global singleton
bus = EventBus()


class Context:
    """Base class for all context-aware modules.
    Each Context auto-registers with the GlobalContext registry.
    """

    def __init__(self, name: str):
        self.name = name
        self._event_bus = bus
        self._unsubscribers: List[Callable] = []
        GlobalContext.register(name, self)

    def emit(self, event: str, data: Any = None):
        """Emit an event on the shared bus."""
        self._event_bus.emit(event, data)

    def on(self, event: str, callback: Callable):
        """Subscribe to event. Auto-unsubscribes on context destruction."""
        unsub = self._event_bus.on(event, callback)
        self._unsubscribers.append(unsub)

    def on_bus(self, event: str, callback: Callable):
        """Direct access to the event bus for subscription."""
        return self._event_bus.on(event, callback)

    def destroy(self):
        """Clean up all subscriptions."""
        for unsub in self._unsubscribers:
            unsub()
        self._unsubscribers.clear()
        GlobalContext.unregister(self.name)


class GlobalContext:
    """Registry for all Context instances. Enables dependency injection."""
    _instances: Dict[str, Context] = {}

    @classmethod
    def register(cls, name: str, ctx: Context):
        cls._instances[name] = ctx

    @classmethod
    def unregister(cls, name: str):
        cls._instances.pop(name, None)

    @classmethod
    def get(cls, name: str) -> Context:
        return cls._instances.get(name)

    @classmethod
    def get_bus(cls) -> EventBus:
        return bus

    @classmethod
    def list_all(cls) -> list:
        return list(cls._instances.keys())

    @classmethod
    def emit(cls, event: str, data: Any = None):
        """Shortcut: emit event on global bus."""
        bus.emit(event, data)

    @classmethod
    def on(cls, event: str, callback: Callable):
        """Shortcut: subscribe on global bus."""
        return bus.on(event, callback)

    @classmethod
    def reset(cls):
        """Reset all contexts (for testing)."""
        for ctx in list(cls._instances.values()):
            ctx.destroy()
        cls._instances.clear()

