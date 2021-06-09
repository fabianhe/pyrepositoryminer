import asyncio
from cProfile import Profile
from pstats import Stats
from subprocess import PIPE, Popen

import uvloop

DATA = bytes("\n".join(str(i) for i in range(100000)), "utf-8")
ITERATIONS = 2000


async def run_async_wc() -> bytes:
    p = await asyncio.create_subprocess_exec(
        "wc", "-l", stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    stdout, stderr = await p.communicate(DATA)
    return stdout


def run_sync_wc() -> bytes:
    p = Popen(["wc", "-l"], stdin=PIPE, stdout=PIPE)
    stdout, stderr = p.communicate(DATA)
    return stdout


def main2() -> None:
    uvloop.install()
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(*(run_async_wc() for _ in range(ITERATIONS)))
    )


def main() -> None:
    for _ in range(ITERATIONS):
        run_sync_wc()


if __name__ == "__main__":
    profile = Profile()
    profile.enable()
    main2()
    profile.disable()
    profile_stats = Stats(profile).sort_stats("tottime")
    profile_stats.print_stats()
