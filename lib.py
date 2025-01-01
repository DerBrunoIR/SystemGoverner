
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
        Undefined behaivior if target State is already installed.
        """
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """
        Uninstalls target state from system.
        Undefined behaivior if target State is already uninstalled.
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
        for state in states:
            assert isinstance(state, State), f"expected State object, got '{state}'"
        self.states = states

    def detect(self) -> bool:
        return all(map(lambda s: s.detect(), self.states))

    def install(self):
        for state in self.states:
            state.ensure_installed()

    def uninstall(self):
        for state in self.states:
            state.ensure_uninstalled()


class Parallel(State):
    """
    A State that installes, detectes, and uninstalls multiple other states concurrently.
    """
    # TODO
    # probably a bad idea
    pass


class Try(State):
    """
    State that ignores Exception's from the encapuslated State.
    """

    def __init__(self, state: State):
        self.state = state

    def install(self):
        try:
            self.state.ensure_installed()
        except Exception:
            pass

    def uninstall(self):
        try:
            self.state.ensure_uninstalled()
        except Exception:
            pass

    def detect(self):
        try:
            return self.state.detect()
        except Exception:
            return False


class Invert(State):
    """
    State that switches install and uninstall from the target State, and invertes the detect result.
    """

    def __init__(self, target: State):
        self.target = state

    def install(self):
        self.target.ensure_uninstalled()

    def uninstall(self):
        self.target.ensure_installed()

    def detect(self):
        return not self.target.detect()


class From(State):
    """
    State that installs temporally a dependency State that is required to install the target State.
    """

    def __init__(self, dependency: State, target: State):
        self.dependency = dependency
        self.target = target

    def install(self):
        self.dependency.ensure_installed()
        self.target.ensure_installed()
        self.dependency.ensure_uninstalled()

    def uninstall(self):
        self.target.ensure_uninstalled()

    def detect(self):
        return self.target.detect()


class Print(State):
    """
    State that prints the given message if it is installed or uninstalled.
    Usefull for logging.
    """

    def __init__(self, msg: str):
        self.msg = msg

    def install(self):
        print(self.msg)

    def uninstall(self):
        print(self.msg)

    def detect(self) -> bool:
        return False


class Breakpoint(State):
    """
    State that triggers breakpoints in install, uninstall and detect before entering the encapsulated state.
    """
    def __init__(self, target: State):
        self.target = target

    def install(self): 
        breakpoint()
        self.target.ensure_installed()

    def uninstall(self):
        breakpoint()
        self.target.ensure_uninstalled()

    def detect(self) -> bool:
        breakpoint()
        return self.target.detect()
