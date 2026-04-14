from abc import ABC, abstractmethod


class IOnboardingController(ABC):
    """Presentation contract for onboarding operations."""

    @abstractmethod
    def run(self) -> None:
        pass

