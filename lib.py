
from abc import ABC, abstractmethod


class State(ABC):
    """
    Abstraction for installing, detecting and uninstalling a target state from the system.
    """
    @abstractmethod
    def detect(self) -> bool:
        """
        Returns true if the target state is already installed.
        """
        pass

    @abstractmethod
    def install(self) -> None:
        """
        Installs target state on system.
        """
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """
        Uninstalls target state from system.
        """
        pass

    def ensure_installed(self):
        """
        Convenience method to install target state if not installed.
        """
        if not self.detect():
            self.install()

    def ensure_uninstalled(self):
        """
        Convenience method to uninstall target state if installed.
        """
        if self.detect():
            self.uninstall()


class Chain(State):
    """
    A State for installing, detecting and uninstalling multiple other states.
    """
    def __init__(self, *states: State):
        self.states = states

    def detect(self) -> bool:
        return all(map(lambda s: s.detect(), self.states))

    def install(self):
        for state in self.states:
            if not state.detect():
                state.install()

    def uninstall(self):
        for state in self.states:
            if state.detect():
                state.uninstall()


class Parallel(State):
    """
    A State that installes, detectes, and uninstalls multiple other states concurrently.
    """
    # TODO
    pass


# catches exceptions
class InstallException(Exception):
    """
    Shall be raised if State installation fails.
    """
    pass

class UninstallException(Exception):
    """
    Shall be raised if State uninstallation fails.
    """
    pass

class DetectException(Exception):
    """
    Shall be raised if State detection fails.
    """
    pass

class Try(State):
    """
    State that ignores InstallException, DetectException and UninstallException from the encapuslated State.
    """

    def __init__(self, state: State):
        self.state = state

    def install(self):
        try:
            self.state.install()
        except InstallException:
            pass

    def uninstall(self):
        try:
            self.state.install()
        except InstallException:
            pass

    def detect(self):
        try:
            return self.state.detect()
        except InstallException:
            return False


class Invert(State):
    """
    State that switches install and uninstall from the encapsulated State, and invertes the detect result.
    """

    def __init__(self, state: State):
        self.state = state

    def install(self):
        self.state.uninstall()

    def uninstall(self):
        self.state.install()

    def detect(self):
        return not self.state.detect()
