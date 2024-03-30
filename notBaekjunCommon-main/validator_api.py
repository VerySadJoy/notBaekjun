from pathlib import Path
import stat

class RunnerEnv:
    """
    Define constants and helper functions
    related to the runner's execution environment
    """
    EXPECTED_DIR = Path("/expected")
    OUTPUT_DIR = Path("/actual")
    CHROOT_DIR = Path("/chroot")
    __USR_DIRS = tuple(Path(CHROOT_DIR, "home").iterdir())
    assert len(__USR_DIRS) == 1
    HOME_DIR = __USR_DIRS[0]

    EXPECTED_CONSOLE = EXPECTED_DIR / "cio"
    EXPECTED_FILE = EXPECTED_DIR / "file"

    F_STDIN = "stdin.txt"
    F_STDOUT = "stdout.txt"
    F_STDERR = "stderr.txt"

    DEF_PORT = 55555
    DEF_TIMEOUT = 5 # in seconds

    DIFF_PASS = 0
    DIFF_FAIL = 1
    DIFF_ERR = 2


class JSONable:
    def toDict(self):
        raise NotImplementedError
    @classmethod
    def fromDict(cls, data: dict):
        raise NotImplementedError


class FileResult(JSONable):
    def __init__(self, fname: str, content: str, diff: str, perm: int = -1):
        assert perm < 0 or stat.S_IMODE(perm) == perm
        self.fname = fname
        self.content = content
        self.diff = diff
        self.perm = perm


    def toDict(self):
        return {
            "content": self.content,
            "diff": self.diff,
            "perm": self.perm
        }


    @classmethod
    def fromDict(cls, data: dict):
        assert len(data) == 1
        fname = data.keys()[0]
        res = cls(fname, data[fname]["content"], data[fname]["diff"], data[fname]["perm"])
        return res


class TCResult(JSONable):
    SUCCESS = 0
    FAIL = 1
    TIMEOUT = 2
    ERROR = 3
    VALID_RESULTS = {SUCCESS, FAIL, TIMEOUT, ERROR}

    def __init__(self, result: int, etime: int, pstatus: int):
        assert result in TCResult.VALID_RESULTS
        self.result = result    # TC result
        self.etime = etime      # Execution time
        self.pstatus = pstatus  # Process exit status
        self.cio = ["", ""]     # type: list[str] [stdout, stderr]
        self.fio = []           # type: list[FileResult]


    def stdout(self, output: FileResult):
        assert output.fname == RunnerEnv.F_STDOUT
        self.cio[0] = output


    def stderr(self, output: FileResult):
        assert output.fname == RunnerEnv.F_STDERR
        self.cio[1] = output


    def addFileRes(self, fres: FileResult):
        self.fio.append(fres)


    def toDict(self):
        return {
            "result": self.result,
            "etime": self.etime,
            "pstatus": self.pstatus,
            "cio": {x.fname: x.toDict() for x in self.cio},
            "fio": {x.fname: x.toDict() for x in self.fio}
        }


    @classmethod
    def fromDict(cls, data: dict):
        res = cls(data["result"], data["etime"], data["pstatus"])
        res.cio = [FileResult.fromDict({x: data["cio"][x]}) for x in (RunnerEnv.F_STDOUT, RunnerEnv.F_STDERR)]
        res.fio = [FileResult.fromDict({k: v}) for k, v in data["fio"].items()]
        return res
